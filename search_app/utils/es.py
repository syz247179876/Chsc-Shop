# -*- coding: utf-8 -*-
# @Time  : 2020/8/12 上午8:10
# @Author : 司云中
# @File : sadas sa.py
# @Software: Pycharm
import elasticsearch
import requests

from Emall.loggings import Logging
from search_app.utils.exceptions import ESConnectionError, ESConflict, ESNotFound
from shop_app.models.commodity_models import Commodity
from elasticsearch import Elasticsearch
from django.conf import settings
from search_app import signals

common_logger = Logging.logger('django')
search_logger = Logging.logger('search_')


class ElasticSearchOperation:
    """直接对es的请求封装(已经抛弃)"""

    # __slots__ = ('query', '_instance', 'url', 'request')
    Model = Commodity

    BASE_URL = 'http://192.168.0.105:9200/'
    FUNC = '_search'
    INDEX_DB = 'shop'

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def combine_url(self):
        """组合url"""
        assert hasattr(self, 'request'), 'Should include request '
        if hasattr(self, 'url'):
            return self.url
        query = self.request.query_params.copy()
        # 生成访问es的url
        credential = {'text': query.get('text')}
        url = self.BASE_URL + self.INDEX_DB + '/' + self.FUNC + '?' + '&'.join(
            ['q=' + key + ':' + value for key, value in credential.items()])
        setattr(self, 'url', url)
        return url

    def get_search_results(self):
        """发送请求,获取索引库的商品id"""
        if hasattr(self, 'pk_list'):
            return self.pk_list
        url = self.combine_url()
        response = requests.get(url).json()
        hits = response.get('hits').get('hits')
        pk_list = [int(document.get('_source').get('django_id')) for document in hits]
        setattr(self, 'pk_list', pk_list)
        return pk_list

    def get_queryset(self):
        """根据索引结果查询数据库"""
        assert hasattr(self, 'Model'), 'Should define Model'
        pk_list = self.get_search_results()
        ordering = 'FIELD(`id`, {})'.format(','.join([str(pk) for pk in pk_list]))  # 设定排序
        return self.Model.commodity_.filter(pk__in=pk_list).extra(select={"ordering": ordering}, order_by=("ordering",))


def error_handler(func):
    """es异常处理装饰器"""

    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except elasticsearch.ConnectionError as e:
            search_logger.error(e)
            raise ESConnectionError()
        except elasticsearch.ConflictError:
            raise ESConflict()
        except elasticsearch.NotFoundError:
            raise ESNotFound()

    return wrap


class ChoiceConf(object):
    """
    根据选项选择配置方式
    mode：[单点，集群, 分片...]
    :param mode: 选项
    :return: 配置dict
    """
    ES_SETTINGS = settings.ELASTICSEARCH_SETTINGS

    def __call__(self, mode=None):
        """回调对象，根据mode选择配置文件"""
        mode = mode or settings.ELASTICSEARCH_CONFIG_MODE
        if mode == 0:
            return self.single
        elif mode == 1:
            return self.cluster

    @property
    def single(self):
        """获取配置文件中的单点配置"""
        return self.ES_SETTINGS.get('single')

    @property
    def cluster(self):
        """获取配置文件中的集群配置"""
        return self.ES_SETTINGS.get('cluster')


choice_conf = ChoiceConf()


class BaseESOperation(object):
    """ES操作基类"""
    _settings = choice_conf

    _instance = None
    _es = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._es = Elasticsearch(**cls._settings())
        return cls._instance

    @property
    def instance(self):
        """获取操作实例"""
        return self._instance

    @property
    def es(self):
        """获取es操作实例"""
        return self._es

    @property
    def is_connect(self):
        """判断是否正常连接"""
        return self.es.ping()

    @property
    def info(self):
        """获取集群详细信息"""
        return self.es.info()

    @error_handler
    def create_indices(self, name, *args, **kwargs):
        """
        创建一个索引库
        :param name: 索引名
        :param ignore_code: 忽略的状态码
        :return: code, result
        """
        kwargs.pop('signal')
        self.es.indices.create(index=name, *args, **kwargs)
        return 200, "创建成功"

    @error_handler
    def create_doc(self, index, id, body, *args, **kwargs):
        """
        在指定索引库中创建一条文档,如果id值相同则返回409冲突错误
        :param index: 索引名
        :param id: document的id
        :param body: document体
        :param args: 其余参数
        :param kwargs: 其余参数
        :return: code, result
        """
        print(index, id, body, args, kwargs)
        self.es.create(index, id, body, *args, **kwargs)
        return 200, "创建成功"

    @error_handler
    def count_doc(self, body, index, *args, **kwargs):
        """
        返回匹配到的documents的个数
        :param body: 查询DSL
        :param index: 索引名
        :param args: 额外参数
        :param kwargs: 额外参数
        :return: code, result
        """
        res = self.es.count(body, index, *args, **kwargs)
        return 200, res['count']

    @error_handler
    def search_doc(self, index, body, *args, **kwargs):
        """
        返回搜索的具体信息
        :param body: 查询DSL
        :param index: 索引库id列表
        :param args: 额外参数
        :param kwargs: 额外参数
        :return: code, result
        """
        return 200, self.es.search(body, index, *args, **kwargs)

    @error_handler
    def delete_doc(self, index, id, *args, **kwargs):
        """
        从指定的索引库中删除指定id的索引项
        :param index: 索引库名
        :param id: document的id
        :param args: 额外参数
        :param kwargs: 额外参数
        :return: code, result
        """
        return 200, self.es.delete(index, id, *args, **kwargs)

    @error_handler
    def update_doc(self, index, id, body, *args, **kwargs):
        """
        更新指定document的数据项
        :param index: 索引库名
        :param id: document的id
        :param body: DSL表达式
        :param args: 额外参数
        :param kwargs: 额外参数
        :return:
        """
        self.es.update(index, id, body, *args, **kwargs)


class CommodityESSearch(BaseESOperation):
    """商品相关信息搜索"""

    def __init__(self):
        super().__init__()
        self.connect()

    def connect(self):
        """注册信号"""
        signals.add_to_es.connect(self.add_to_es, sender=None)
        signals.delete_from_es.connect(self.delete_from_es, sender=None)
        signals.update_to_es.connect(self.update_to_es, sender=None)
        signals.retrieve_from_es.connect(self.retrieve_from_es, sender=None)

    def add_to_es(self, sender, id, body, *args, **kwargs):
        """
        向es的索引库中添加新的记录
        :param sender: index索引库名
        :param id: doc的id
        :param body: DSL表达式
        :param args: 额外参数
        :param kwargs: 额外参数
        :return: code, result
        """
        kwargs.pop('signal')
        return self.create_doc(sender, id, body, *args, **kwargs)

    def delete_from_es(self, sender, id, *args, **kwargs):
        """
        从es的索引库删除指定id的记录
        :param sender: index索引库名
        :param id:doc的id
        :param args: 额外参数
        :param kwargs: 额外参数
        :return: code, result
        """
        kwargs.pop('signal')
        return self.delete_doc(sender, id, *args, **kwargs)

    def update_to_es(self, sender, id, body, *args, **kwargs):
        """
        在es的索引库中更新指定id的记录
        :param sender: index索引库名
        :param id: doc的id
        :param body: DSL表达式
        :param kwargs: 额外参数
        :return: code, result
        """
        kwargs.pop('signal')
        return self.update_doc(sender, id, body, *args, **kwargs)

    def retrieve_from_es(self, sender, body, *args, **kwargs):
        """
        从es的索引库中搜索出满足DSL表达式的记录
        :param sender: index索引库名
        :param body: doc的id
        :param args: DSL表达式
        :param kwargs: 额外参数
        :return: code, result
        """
        kwargs.pop('signal')
        return self.search_doc(sender, body, *args, **kwargs)


commodity_es = CommodityESSearch()
