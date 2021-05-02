# -*- coding: utf-8 -*-
# @Time  : 2021/4/13 下午2:30
# @Author : 司云中
# @File : diplay_serializers.py
# @Software: Pycharm


from rest_framework import serializers

from Emall.loggings import Logging
from remark_app.models.remark_models import Remark, RemarkReply
from seller_app.models import Store
from shop_app.models.commodity_models import Commodity, SkuProps, SkuValues, Freight, FreightItem, CommodityCategory
from user_app.model.collection_models import Collection

consumer_logger = Logging.logger('consumer_')


class CommodityCardSerializer(serializers.ModelSerializer):
    """商品卡片显示序列化器"""

    store_name = serializers.CharField(source='store.name')
    is_free = serializers.BooleanField(source='freight.is_free')

    class Meta:
        model = Commodity
        fields = ('pk', 'commodity_name', 'price', 'favourable_price', 'details', 'intro', 'little_image',
                  'sell_counts', 'store_name', 'is_free')


class CommodityRemarkReplySerializer(serializers.ModelSerializer):
    """商品的评价回复序列化器"""

    class Meta:
        model = RemarkReply
        fields = ('reply_content', 'reply_time', 'praise', 'against', 'is_action')


class CommodityRemarkSerializer(serializers.ModelSerializer):
    """商品的评价序列化器"""
    consumer = serializers.CharField(read_only=True, source='consumer.username')
    reply = CommodityRemarkReplySerializer(many=True)

    class Meta:
        model = Remark
        fields = ('consumer', 'grade', 'reward_content', 'reward_time', 'praise', 'against', 'action_status', 'reply')


class CommodityFreightItemSerializer(serializers.ModelSerializer):
    """商品运费模板项序列化器"""

    class Meta:
        model = FreightItem
        fields = '__all__'


class CommodityFreightSerializer(serializers.ModelSerializer):
    """商品运费模板序列化器"""

    freight_items = CommodityFreightItemSerializer(many=True)

    class Meta:
        model = Freight
        fields = '__all__'


class CommodityStoreSerializer(serializers.ModelSerializer):
    """指定商品所属的店铺的信息序列化器"""

    class Meta:
        model = Store
        fields = '__all__'


class CommoditySkuValuesSerializer(serializers.ModelSerializer):
    """指定商品的sku的属性值序列化器"""

    # 商品默认可以选中,为False就是不可选中,表示多个类目属性组成sku无效
    status = serializers.BooleanField(default=True)

    # 商品是否可以被选中,默认没被选中
    is_choice = serializers.BooleanField(default=False)

    class Meta:
        model = SkuValues
        fields = '__all__'


class CommoditySkuPropsSerializer(serializers.ModelSerializer):
    """指定商品的sku的属性序列化器"""

    sku_values = CommoditySkuValuesSerializer(many=True)

    class Meta:
        model = SkuProps
        fields = '__all__'


class CommodityDetailSerializer(serializers.ModelSerializer):
    """商品详情页信息序列化器"""

    sku_props = CommoditySkuPropsSerializer(many=True)
    store = CommodityStoreSerializer()
    freight = CommodityFreightSerializer()
    remark = CommodityRemarkSerializer(many=True)

    collection = serializers.SerializerMethodField()

    def get_collection(self, obj):
        """
        判断该商品用户是否收藏
        """
        user = getattr(self.context.get('request'), 'user', None)
        data = {
            'is_collected': False,
            'pk': None
        }
        if not user:
            return data
        else:
            queryset = Collection.objects.filter(commodity_id=obj.pk, user=user)
            if queryset.exists():
                object = queryset.first()
                data['is_collected'] = True
                data['pk'] = object.pk
            return data

    class Meta:
        model = Commodity
        fields = '__all__'


class CommodityFirstCategorySerializer(serializers.ModelSerializer):
    """商品一级类别序列化器"""

    text = serializers.CharField(source='name')  # 换名

    class Meta:
        model = CommodityCategory
        fields = ('pk', 'text')


class CommoditySecondCategorySerializer(serializers.ModelSerializer):
    """商品二级及以下序列化器"""

    child = serializers.SerializerMethodField(read_only=True)

    def get_child(self, obj):
        """
        对自身递归嵌套查询
        注意obj此时为字典类型,每次递归要跟第三次一样
        """
        return CommoditySecondCategorySerializer(instance=self.Meta.model.objects.filter(pre_id=obj.get('pk'))
                                                 .values('pk', 'name', 'thumbnail').order_by('sort'), many=True).data

    class Meta:
        model = CommodityCategory
        fields = ('pk', 'name', 'thumbnail', 'child')  # pre会反序列化为model实例
        read_only_fields = ('pk', 'name', 'thumbnail', 'child')
