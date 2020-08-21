# -*- coding: utf-8 -*- 
# @Time : 2020/5/27 21:40 
# @Author : 司云中 
# @File : favorites_redis.py 
# @Software: PyCharm
import datetime
import json
import pickle
import time

from django.core import serializers
from django.dispatch import receiver

from Shop_app.models.commodity_models import Commodity
from User_app import signals
from User_app.models.user_models import Collection
from User_app.signals import add_favorites, delete_favorites
from e_mall.base_redis import BaseRedis
from e_mall.json_serializer import JsonCustomEncoder
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class RedisFavoritesOperation(BaseRedis):
    """the operation of Favorites about redis"""

    def __init__(self, redis_instance):
        self.connect()
        super().__init__(redis_instance)

    def zset_key_store(self, user_pk):
        """收藏夹zset的键"""
        return self.key('favorites', user_pk, 'store')

    def zset_key_commodity(self, user_pk):
        return self.key('favorites', user_pk, 'commodity')

    def hash_key_store(self, user_pk, collection_pk):
        """收藏夹中店铺的hash键"""
        return self.key('favorites', user_pk, 'store', collection_pk)

    def hash_key_commodity(self, user_pk, collection_pk):
        """收藏夹中商品的hash键"""
        return self.key('favorites', user_pk, 'commodity', collection_pk)

    def connect(self):
        signals.add_favorites.connect(self.sync_favorites_add_callback, sender=Collection)
        signals.delete_favorites.connect(self.sync_favorites_delete_callback, sender=Collection)

    def get_resultSet(self, user, page, page_size, **kwargs):
        """
        考虑缓存击穿：即使空结果集也放到缓存中去
        redis使用有序集合+hash表+List实现数据存储和获取
        确保有序，使用有序集合，在redis层面提升排序性能
        :return: list（读取redis)， 查询集（读取mysql）
        """
        user_pk = user.pk
        zset_key = self.zset_key_commodity(user_pk)
        collection_dict = {int(key.decode()): value for key, value in
                           self.redis.zrevrange(zset_key, (page - 1) * page_size, page * page_size, withscores=True)}

        if collection_dict:  # 缓存命中,寻找对应的商品hash表
            list_resultSet = []
            if 0 in collection_dict:  # 如果数据库未命中，缓存中的0代表空数据
                return 'null'
            for key in collection_dict:
                hash_key = self.hash_key_commodity(user_pk, key)
                offset, hresult = self.redis.hscan(hash_key)
                if offset != 0:
                    hresult.update(self.redis.hscan(hash_key, cursor=offset))  # 从上一次的offset中读取,防止hscan一次性没读完
                list_resultSet.append(hresult)
            # list扔到任务队列中去将字典中的bytes-->str,解析，转换成我需要的数据格式
            # list_result_format = format_data.apply_async(args=(list_resultSet,))  # 异步任务反而变慢了，不接受byte数据
            list_result_format = self.deserializer_commodity_data(list_resultSet)  # 反序列化
            return list_result_format

        # 为命中缓存
        queryset = Collection.collection_.select_related('commodity').filter(user=user)[
                   (page - 1) * page_size: page * page_size]
        pipe_two = self.redis.pipeline()  # 建立管道

        commodity_list = [query.commodity for query in queryset]  # 商品查询集
        serializer_commodity = serializers.serialize('python', commodity_list)  # 对商品集序列化
        for serializer, query in zip(serializer_commodity, queryset):  # 将同迭代次数的可迭代元素打包程元祖
            commodity_pk = serializer.get('pk')  # 获取每个商品的pk
            commodity_fields = serializer.get('fields')  # 获取每个商品的fields
            commodity_fields.update({'pk': commodity_pk})  # 将pk添加进fields字典中
            collection_pk = query.pk  # 收藏记录的pk
            pipe_two.zadd(zset_key, {collection_pk: time.time()})  # 添加到有序集合中
            pipe_two.expire(zset_key, 30)  # 设置30sTTL
            hash_value_commodity = self.hash_key_commodity(user_pk, collection_pk)
            pipe_two.hmset(hash_value_commodity, self.serializer_commodity_data(commodity_fields))  # 将商品信息添加到hash表中
            pipe_two.expire(hash_value_commodity, 30)
        pipe_two.execute()

        return queryset  # 返回商品查询集

    # def delete_favorites_goods_id(self, user, **kwargs):
    #     """
    #     delete id of goods which in favorites into redis
    #     :param user_id: 商品id
    #     :param data: request.data的Querydict实例
    #     :return:是否删除成功
    #     """
    #     key = self.zset_key_commodity(user.pk)
    #     if 'is_all' not in kwargs:
    #         commodity_id = int(kwargs.get('commodity_id')[0])
    #         delete_counts = self.redis.lrem(key, commodity_id)  # delete commodity_id from the list once
    #     else:
    #         delete_counts = self.redis.delete(key)  # delete this key
    #     self.redis.close()
    #     return True if delete_counts else False

    def serializer_commodity_data(self, data):
        """
        序列化数据
        将model序列化后的数据格式化成合格的json格式，以便添加到redis中的hash
        """
        result = json.loads(json.dumps(data, cls=JsonCustomEncoder))
        for key, value in result.items():
            if result[key] is None:  # 因为redis不接受null，必须化成0/1, 商品上架状态
                result[key] = 'null'
            elif result[key] == True:  # 因为redis不接受bool，必须化成0/1, 商品上架状态
                result[key] = 1
            elif result[key] == False:
                result[key] = 0
        return result

    @staticmethod
    def deserializer_commodity_data(data):
        """反序列化"""
        if isinstance(data, list):
            data = [{key.decode(): value.decode() for key, value in orderdict.items() if key.decode() not in ['store','shopper','onshelve_time', 'unshelve_time']} for
                    orderdict in data]
        # TODO 将redis中的数据序列化为分页器格式

        return data

    # @receiver(add_favorites, sender=Collection)
    def sync_favorites_add_callback(self, sender, instance, user, queryset, **kwargs):
        """
        同步redis中的favorites数据，信号回调函数
        添加到zset和hash表中
        :param sender: 发送方Collection
        :param instance: 创建的Collection实例
        :param user: 当前登录的用户
        :param queryset: 当前用户收藏的商品/种类/其他
        :param kwargs: 额外参数
        :return:  同步是否成功, bool
        """
        user_pk = user.pk
        zset_key = self.zset_key_commodity(user_pk)
        serialized_commodity = serializers.serialize('python', queryset)  # 序列化商品
        pipe = self.redis.pipeline()  # 开启管道
        if serialized_commodity:
            collection_pk = instance.pk  # collection的pk
            fields = serialized_commodity[0].get('fields')
            fields.update({'pk': serialized_commodity[0].get('pk')})
            timestamp = time.time()
            pipe.zadd(zset_key, {collection_pk: timestamp})  # 向有序集合中添加收藏夹元素
            hash_key_store = self.hash_key_commodity(user_pk, collection_pk)
            pipe.hmset(hash_key_store, self.serializer_format_hash(fields))  # 深度格式成JSON数据
            pipe.expire(zset_key, 30)  # 过期时间30s
            pipe.expire(hash_key_store, 30)
        pipe.execute()
        self.redis.close()

    # 动态跟着回调函数注册
    # @receiver(delete_favorites, sender=Collection)
    def sync_favorites_delete_callback(self, sender, user, collection_pk=None, is_all=False, **kwargs):
        """
        同步删除redis中的favorites数据，信号回调函数
        """
        user_pk = user.pk
        zset_key = self.zset_key_commodity(user_pk)
        pipe = self.redis.pipeline()
        if is_all:
            collection_list = (value.decode() for value in self.redis.zrange(zset_key, 0, -1))  # 返回所有的商品id列表，用于删除hash表
            pipe.delete(zset_key)  # 删除zset中目标收藏的商品的元素
            for pk in collection_list:
                hash_temp_key = self.hash_key_commodity(user_pk, pk)
                pipe.delete(hash_temp_key)
        else:
            hash_key = self.hash_key_commodity(user, collection_pk)
            pipe.zrem(zset_key, collection_pk)
            pipe.delete(hash_key)  # 删除某一个hash表
        pipe.execute()
        self.redis.close()


favorites_redis = RedisFavoritesOperation.choice_redis_db('redis')
