# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:38
# @Author : 司云中
# @File : commodity_serializers.py
# @Software: Pycharm
import json

from django.db import DatabaseError, transaction, DataError, IntegrityError
from django.db.models import ProtectedError
from django.db.transaction import atomic
from rest_framework import serializers

from Emall.exceptions import DataFormatError, SqlServerError, DataNotExist, DataTypeError, SqlConstraintError
from Emall.loggings import Logging
from search_app.signals import add_to_es, update_to_es
from seller_app.models import Seller
from shop_app.models.commodity_models import Commodity, CommodityCategory, Freight, SkuProps, SkuValues, \
    FreightItem, Sku
from django.conf import settings

commodity_logger = Logging.logger('commodity_')


class CommodityCategorySerializer(serializers.ModelSerializer):
    """商品类别序列化器"""

    children = serializers.SerializerMethodField()
    value = serializers.IntegerField(source='pk')
    label = serializers.CharField(source='name')

    class Meta:
        model = CommodityCategory
        fields = ('value', 'label', 'children')

    def get_children(self, obj):
        # 如果当前类别有后继结点的话,则继续递归查找所有前驱结点为该结点pk值的子类别,递归嵌套
        if obj.has_next:
            return CommodityCategorySerializer(instance=self.Meta.model.objects.filter(pre=obj.pk), many=True).data
        else:
            return None


class CommodityFreightSerializer(serializers.ModelSerializer):
    """商品运费模板序列化器（简易版）"""

    charge_type = serializers.CharField(source='get_charge_type_display')

    class Meta:
        model = Freight
        fields = ('pk', 'name', 'is_free', 'charge_type')

class SellerCommoditySerializer(serializers.ModelSerializer):
    """商家操作商品模型序列化器"""

    # category_list = serializers.SerializerMethodField()

    # 分组列表,写
    groups = serializers.ListField(child=serializers.CharField(max_length=10), write_only=True, allow_empty=True)

    # 种类id
    category_id = serializers.IntegerField(min_value=1)

    # 模板id
    freight_id = serializers.IntegerField(min_value=1)

    # 库存量
    stock = serializers.IntegerField(min_value=1, required=True)

    # 商品详情页顶部轮播大图片的完整路径
    big_image = serializers.CharField(required=True)

    # 商品的标志图片的完整路径
    little_image = serializers.CharField(max_length=256, required=True)

    class Meta:
        model = Commodity
        category_model = CommodityCategory
        seller_model = Seller
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'intro', 'groups',
                  'status', 'stock', 'category_id', 'freight_id', 'details', 'spu', 'big_image', 'little_image')
        read_only_fields = ('pk',)


    def add_update_dsl(self, id, index=None, **kwargs):
        """
        添加商品的dsl表达式
        :param id: 商品id
        :param index: 索引库名，可自定义/从配置文件读
        :param kwargs: 其他body参数
        :return:
        """
        return dict(sender=index or settings.ES_INDICES.get('default'), id=id, body=kwargs)

    def search_body(self, commodity):
        """
        构造/修改es搜索的关键字体
        索引体中存放商品名，商品简介，商品类别
        :param commodity: 商品instance
        :return: dict
        """
        return {
            'commodity_name': commodity.commodity_name,
            'intro': commodity.intro,
            'category': commodity.category.name  # 这里要优化，防止再次hit数据库
        }

    def update_script(self, commodity):
        """使用script来对document进行更新"""
        return {
            "doc": {
                'commodity_name': commodity.commodity_name,
                'intro': commodity.intro,
                'category': commodity.category.name  # 这里要优化，防止再次hit数据库
            }
        }

    def add_commodity(self):
        """商家添加商品"""
        try:
            with transaction.atomic():
                commodity = self.Meta.model(**self.get_credential)
                commodity.save()
                commodity.group.add(*self.validated_data.pop('groups'))
        except DatabaseError:
            raise SqlServerError()
        else:
            # 发送信号,添加document到索引库
            add_to_es.send(**self.add_update_dsl(commodity.pk, **self.search_body(commodity)))

    def update_commodity(self):
        """商家修改商品"""
        pk = self.context.get('request').data.get('pk', None)
        if not pk:
            raise DataFormatError("缺少必要的数据")
        credential = self.get_credential
        queryset = self.Meta.model.commodity_.filter(pk=pk)
        updated_rows = queryset.update(**credential)
        print(updated_rows)
        # 发送信号，如果作用记录>0, 更新索引库中id对应的document
        if updated_rows:
            update_to_es.send(**self.add_update_dsl(queryset.first().pk, **self.update_script(queryset.first())))
            return updated_rows
        return 0

    @property
    def get_credential(self):
        """获取需要的数据集"""
        user = self.context.get('request').user
        seller = self.Meta.seller_model.objects.select_related('store').get(user=user)
        return {
            'user': user,
            'store': seller.store,
            'category_id': self.validated_data.pop('category_id'),
            'freight_id': self.validated_data.pop('freight_id'),
            'commodity_name': self.validated_data.pop('commodity_name'),
            'price': self.validated_data.pop('price'),
            'favourable_price': self.validated_data.pop('favourable_price'),
            'details': self.validated_data.pop('details', ''),
            'intro': self.validated_data.pop('intro'),
            'status': self.validated_data.pop('status'),
            'stock': self.validated_data.pop('stock'),
            'spu': self.validated_data.pop('spu', ''),
            'big_image': self.validated_data.pop('big_image'),
            'little_image': self.validated_data.pop('little_image')
        }


class SellerCommodityPicSerializer(serializers.Serializer):
    """商品图片相关序列化器"""
    pic_list = serializers.ListField(child=serializers.CharField(max_length=256), allow_null=False)

    class Meta:
        mode = Commodity
        fields = ('pic_list')

    def append_pic(self):
        """追加图片完整路径名"""
        pic_str = ';'.join(self.validated_data.pop('pic_list'))
        rows = self.Meta.mode.commodity_.filter()



class SellerCommodityDeleteSerializer(serializers.Serializer):
    class Meta:
        model = Commodity

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def delete_commodity(self):
        """商家删除商品"""
        rows, _ = self.Meta.model.commodity_.filter(pk__in=self.validated_data.pop('pk_list')).delete()
        return rows

class SkuValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkuValues
        fields = ('pk', 'value')


class SkuPropSerializer(serializers.ModelSerializer):
    """sku 属性:[属性值,]序列化器"""

    sku_values = serializers.ListField(child=serializers.CharField(max_length=20), allow_empty=False, write_only=True)

    values = serializers.SerializerMethodField()  # 显示属性对应的值数组

    commodity_name = serializers.CharField(source='commodity.commodity_name', read_only=True)

    cid = serializers.IntegerField(source='commodity.pk', read_only=True)

    class Meta:
        model = SkuProps
        values_model = SkuValues
        fields = ('pk', 'name', 'sku_values', 'values', 'commodity', 'commodity_name', 'cid')
        read_only_fields = ('pk',)

    def get_values(self, obj):
        values = self.Meta.values_model.objects.filter(prop=obj)
        return SkuValueSerializer(values, many=True).data

    def add(self):
        """添加sku属性规格和值"""
        credential = {
            'name': self.validated_data.pop('name'),
            'sku_values': self.validated_data.pop('sku_values'),
            'commodity': self.validated_data.pop('commodity')
        }

        try:
            with atomic():  # 开启事务
                prop = self.Meta.model.objects.create(name=credential.pop('name'),
                                                      commodity=credential.pop('commodity'))
                self.Meta.values_model.objects.bulk_create([
                    self.Meta.values_model(value=value, prop=prop) for value in
                    credential.pop('sku_values')
                ])
        except DatabaseError:
            raise SqlServerError('数据错误')

    def modify(self):
        """修改商品属性规格和值"""
        credential = {
            'name': self.validated_data.pop('name'),
            'sku_values': self.validated_data.pop('sku_values')
        }
        try:
            with atomic():
                # 先全部删除,然后重新添加
                prop = self.Meta.model.objects.get(pk=self.context.get('request').data.get('pk'))  # 存在一个BUG
                self.Meta.values_model.objects.filter(prop=prop).delete()
                self.Meta.values_model.objects.bulk_create([
                    self.Meta.values_model(value=value, prop=prop) for value in
                    credential.pop('sku_values')
                ])
        except DataError:
            raise SqlServerError()
        except self.Meta.model.DoesNotExist:
            raise DataNotExist()


class SkuPropsDeleteSerializer(serializers.Serializer):
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    class Meta:
        model = SkuProps

    def delete(self):
        """删除商品属性规格和值"""
        return self.Meta.model.objects.filter(pk__in=self.validated_data.pop('pk_list')).delete()


class SkuCommoditySerializer(serializers.ModelSerializer):
    """与Sku有关的商品数据序列化器"""

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name')


class FreightItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreightItem
        fields = ('pk', 'freight', 'status', 'first_piece', 'continue_piece', 'first_price', 'continue_price', 'city')
        read_only_fields = ('pk',)

    def add(self):
        return self.Meta.model.objects.create(**self.validated_data)


class FreightSerializer(serializers.ModelSerializer):
    freight_items_w = serializers.ListField(child=serializers.DictField(allow_empty=False), allow_empty=False,
                                            write_only=True)  # 运费项
    pk = serializers.IntegerField(min_value=1, required=False)  # 解决找不到pk问题

    str_charge_type = serializers.SerializerMethodField()

    str_is_free = serializers.SerializerMethodField()

    freight_items = FreightItemSerializer(many=True, read_only=True)

    def get_str_is_free(self, obj):
        return '包邮' if obj.is_free else '不包邮'

    def get_str_charge_type(self, obj):
        return obj.get_charge_type_display()

    class Meta:
        model = Freight
        item_model = FreightItem
        fields = (
            'pk', 'name', 'str_is_free', 'str_charge_type', 'freight_items_w', 'is_free', 'charge_type',
            'freight_items')
        read_only_fields = ('pk',)

    def add(self):
        """添加新的运费模板"""
        credential = {
            'name': self.validated_data.pop('name'),
            'is_free': self.validated_data.pop('is_free'),
            'charge_type': self.validated_data.pop('charge_type'),
            'user': self.context.get('request').user
        }

        try:
            with transaction.atomic():
                freight = self.Meta.model.objects.create(**credential)  # 创建运费模板
                freight_item_data = self.validated_data.pop('freight_items_w')
                # 双层嵌套,批量创建运费项和运费城市项， 创建运费项， 创建运费城市项
                freight_items = [self.Meta.item_model(freight=freight, **item) for item in freight_item_data]
                self.Meta.item_model.objects.bulk_create(freight_items)
        except DatabaseError as e:
            commodity_logger.error(e)
            raise SqlServerError()

    def modify(self):
        """
        原有基础上修改运费模板，不添加/删除运费项
        数据结构清晰，优化查询条件
        """
        credential = {
            'pk': self.validated_data.pop('pk'),
            'name': self.validated_data.pop('name'),
            'is_free': self.validated_data.pop('is_free'),
            'charge_type': self.validated_data.pop('charge_type'),
        }

        try:
            queryset = self.Meta.model.objects.filter(pk=credential.pop('pk'))
            rows = queryset.count()
            # 数据不存在
            if rows == 0:
                raise DataNotExist()
            freight_item_data = self.validated_data.pop('freight_items_w')
            # 临时存放对象
            temp_objs_item = []
            # 更新运费项记录
            for item in freight_item_data:
                # 遍历list，元素为item字典
                # TODO: 这里还需要加强校验
                item_obj = self.Meta.item_model.objects.get(pk=item.pop('pk'), freight=queryset.first())  # 获取item对象
                item_obj.first_piece = item.pop('first_piece')
                item_obj.continue_piece = item.pop('continue_piece')
                item_obj.first_price = item.pop('first_price')
                item_obj.continue_price = item.pop('continue_price')
                item_obj.city = item.pop('city')
                item_obj.status = item.pop('status')
                temp_objs_item.append(item_obj)  # 追加进去，批量更新
            # 开启事务
            with transaction.atomic():
                queryset.update(**credential)  # 更新运费模板记录
                # 批量处理
                self.Meta.item_model.objects.bulk_update(temp_objs_item,
                                                         ['first_piece', 'continue_piece', 'first_price',
                                                          'continue_price', 'city', 'status'])
                del temp_objs_item
        except self.Meta.item_model.DoesNotExist:
            raise DataNotExist()
        except DatabaseError as e:
            # 其他数据库更新错误
            commodity_logger.error(e)
            raise SqlServerError()

    def validate_freight_item(self, value):
        """
        校验运费项字典
        :param value: value
        :return: Bool
        """
        if self.context['request'].method.lower() == 'put':
            for item in value:
                if 'pk' not in item:
                    raise DataFormatError('数据缺失')
        elif self.context['request'].method.lower() == 'post' and 'pk' in value:
            raise DataFormatError('数据过多')
        return value


class FreightDeleteSerializer(serializers.Serializer):
    """
    删除运费模板序列化器
    """

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    class Meta:
        model = Freight

    def delete(self):
        try:
            return self.Meta.model.objects.filter(pk__in=self.validated_data.pop('pk_list')).delete()
        except ProtectedError:
            raise SqlServerError('存在商品使用该模板，无法删除！')


class SellerSkuSerializer(serializers.ModelSerializer):
    """
    商家管理有效SKU序列化器
    """

    properties_r = serializers.SerializerMethodField()  # 用于读

    properties_w = serializers.DictField(child=serializers.CharField(), allow_empty=False, write_only=True)  # 用于写

    commodity_name = serializers.CharField(source='commodity.commodity_name', read_only=True)

    cid = serializers.IntegerField(source='commodity.pk', read_only=True)

    class Meta:
        model = Sku
        read_only_fields = ('pk',)
        fields = ('pk', 'sid', 'commodity', 'stock', 'price', 'favourable_price', 'image', 'name', 'status',
                  'properties_r', 'properties_w', 'commodity_name', 'cid')

    def get_properties_r(self, obj):
        """将properties反序列化"""
        return json.loads(obj.properties)

    def add(self):
        """添加有效SKU"""
        self.validated_data['properties'] = json.dumps(self.validated_data.pop('properties_w'))
        self.Meta.model.objects.create(**self.validated_data)

    def modify(self):
        """修改有效SKU"""
        pk = self.context.get('request').data.get('pk', None)
        if not pk:
            raise DataFormatError('缺少数据')
        self.validated_data['properties'] = json.dumps(self.validated_data.pop('properties_w'))
        rows = self.Meta.model.objects.filter(pk=pk).update(**self.validated_data)
        return rows


class SellerSkuDeleteSerializer(serializers.Serializer):
    """
    删除有效SKU序列化器
    """
    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    class Meta:
        model = Sku

    def delete(self):
        """删除有效SKU"""
        try:
            return self.Meta.model.objects.filter(pk__in=self.validated_data.pop('pk_list')).delete()
        except TypeError:
            raise SqlConstraintError('订单中正使用有效sku，无法删除')
