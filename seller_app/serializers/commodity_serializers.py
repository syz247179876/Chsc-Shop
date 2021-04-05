# -*- coding: utf-8 -*-
# @Time  : 2021/2/17 下午10:38
# @Author : 司云中
# @File : commodity_serializers.py
# @Software: Pycharm
from django.db import DatabaseError, transaction
from django.db.transaction import atomic
from rest_framework import serializers

from Emall.exceptions import DataFormatError, SqlServerError, DataNotExist
from Emall.loggings import Logging
from seller_app.models import Seller
from shop_app.models.commodity_models import Commodity, CommodityCategory, Freight, SkuProps, SkuValues, \
    FreightItem

commodity_logger = Logging.logger('commodity_')


class CommodityCategorySerializer(serializers.ModelSerializer):
    """商品类别序列化器"""

    children = serializers.SerializerMethodField()

    class Meta:
        model = CommodityCategory
        fields = ('name', 'children')

    def get_children(self, obj):

        # 如果当前类别有后继结点的话,则继续递归查找所有前驱结点为该结点pk值的子类别,递归嵌套
        if obj.has_next:
            return CommodityCategorySerializer(self.get_queryset(obj.pk), many=True).data
        else:
            return None

    def get_queryset(self, pre):
        """根据pre查找所属的子类别"""
        return CommodityCategory.objects.filter(pre=pre)


class SellerCommoditySerializer(serializers.ModelSerializer):
    """商家操作商品模型序列化器"""

    category_list = serializers.SerializerMethodField()

    # 分组列表,读
    group_list = serializers.SerializerMethodField()

    # 分组列表,写
    groups = serializers.ListField(child=serializers.CharField(max_length=10), write_only=True, allow_empty=True)

    # 种类id
    category_id = serializers.IntegerField(min_value=1)

    # 模板id
    freight_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Commodity
        category_model = CommodityCategory
        seller_model = Seller
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'intro', 'groups',
                  'status', 'stock', 'category_id',
                  'freight_id', 'category_list', 'group_list')
        read_only_fields = ('pk', 'category_list', 'group_list')

    def get_category_list(self, obj):
        """获取全部的序列化器"""
        category = self.Meta.category_model.objects.all()
        return CommodityCategorySerializer(category, many=True).data

    def add_commodity(self):
        """商家添加商品"""
        try:
            with transaction.atomic():
                commodity = self.Meta.model(**self.get_credential)
                commodity.save()
                commodity.group.add(*self.validated_data.pop('groups'))
        except DatabaseError:
            raise SqlServerError()

    def update_commodity(self):
        """商家修改商品"""
        pk = self.validated_data.pop('pk')
        credential = self.get_credential
        self.Meta.model.commodity_.filter(pk=pk).update(**credential)

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
            'status': self.validated_data.pop('status')
        }


class SellerCommodityDeleteSerializer(serializers.Serializer):
    class Meta:
        model = Commodity

    pk_list = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def delete_commodity(self):
        """商家删除商品"""
        self.Meta.model.commodity_.filter(pk__in=self.validated_data.pop('pk_list')).delete()


class SkuValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkuValues
        fields = ('pk', 'value')


class SkuPropSerializer(serializers.ModelSerializer):
    """sku 属性:[属性值,]序列化器"""

    sku_values = serializers.ListField(child=serializers.CharField(max_length=20), allow_empty=False, write_only=True)

    values = serializers.SerializerMethodField()  # 显示属性对应的值数组

    class Meta:
        model = SkuProps
        values_model = SkuValues
        fields = ('pk', 'name', 'sku_values', 'values')
        read_only_fields = ('pk',)

    def get_values(self, obj):
        values = self.Meta.values_model.objects.filter(prop=obj)
        return SkuValueSerializer(values, many=True).data

    def add(self):
        """添加sku属性规格和值"""
        credential = {
            'name': self.validated_data.pop('name'),
            'sku_values': self.validated_data.pop('sku_values')
        }

        try:
            with atomic():  # 开启事务
                prop = self.Meta.model.objects.create(name=credential.pop('name'))
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
                prop = self.Meta.model.objects.get(pk=self.context.get('request').data.get('pk'))
                self.Meta.values_model.objects.filter(prop=prop).delete()
                self.Meta.values_model.objects.bulk_create([
                    self.Meta.values_model(value=value, prop=prop) for value in
                    credential.pop('sku_values')
                ])
        except DatabaseError():
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


class FreightSerializer(serializers.ModelSerializer):
    freight_item = serializers.ListField(child=serializers.DictField(allow_empty=False), allow_empty=False,
                                         write_only=True)  # 运费项
    pk = serializers.IntegerField(min_value=1)  # 解决找不到pk问题

    class Meta:
        model = Freight
        item_model = FreightItem
        fields = ('pk', 'name', 'is_free', 'charge_type', 'freight_item')

    def add(self):
        """添加新的运费模板"""
        credential = {
            'name': self.validated_data.pop('name'),
            'is_free': self.validated_data.pop('is_free'),
            'charge_type': self.validated_data.pop('charge_type')
        }

        try:
            with transaction.atomic():
                freight = self.Meta.model.objects.create(**credential)  # 创建运费模板
                freight_item_data = self.validated_data.pop('freight_item')
                # 双层嵌套,批量创建运费项和运费城市项， 创建运费项， 创建运费城市项
                freight_items = [self.Meta.item_model(freight=freight, **item) for item in freight_item_data]
                print(type(freight_items[0]))  # 检查类型
                self.Meta.item_model.objects.bulk_create(freight_items)
        except DatabaseError as e:
            commodity_logger.error(e)
            raise SqlServerError()

    def modify(self):
        """
        修改运费模板
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
            freight_item_data = self.validated_data.pop('freight_item')
            # 临时存放对象
            temp_objs_item = []
            # 更新运费项记录
            for item in freight_item_data:
                # 遍历list，元素为item字典
                item_obj = self.Meta.item_model.objects.get(pk=item.pop('pk'), freight=queryset.first())  # 获取item对象
                item_obj.first_piece = item.pop('first_piece')
                item_obj.continue_piece = item.pop('continue_piece')
                item_obj.first_price = item.pop('first_price')
                item_obj.continue_price = item.pop('continue_price')
                item_obj.city = item.pop('city')
                temp_objs_item.append(item_obj)  # 追加进去，批量更新
            # 开启事务
            with transaction.atomic():
                queryset.update(**credential)  # 更新运费模板记录
                # 批量处理
                self.Meta.item_model.objects.bulk_update(temp_objs_item,
                                                         ['first_piece', 'continue_piece', 'first_price',
                                                          'continue_price', 'city'])
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
        return self.Meta.model.objects.filter(pk__in=self.validated_data.pop('pk_list')).delete()
