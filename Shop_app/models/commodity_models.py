from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Manager
# Create your models here.
from django.utils.html import format_html

from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField
from Shopper_app.models.shopper_models import Store, Shoppers
from User_app.models.user_models import Consumer
from ..validators import *


class Commodity(models.Model):
    """商品表"""
    # 店铺
    store = models.ForeignKey(Store,
                              verbose_name=_('商铺'),
                              help_text=_('商品所在的店铺'),
                              on_delete=models.CASCADE,
                              related_name='commodity',
                              )
    # 店家
    shopper = models.ForeignKey(User,
                                verbose_name=_('商家'),
                                help_text=_('商品所属的商家'),
                                on_delete=models.CASCADE,
                                related_name='commodity',
                                )

    # 商品名称
    commodity_name = models.CharField(verbose_name=_('商品名称'),
                                      help_text=_('Please enter the name of the product'),
                                      max_length=50,
                                      validators=[CommodityValidator(), ]
                                      )
    # 商品价格,正整数
    price = models.PositiveIntegerField(verbose_name=_('价格'),
                                        help_text=_('Please enter the price of the goods'),
                                        validators=[MaxValueValidator(999999, message=_('商品最高价格不能高于999999'))]
                                        )
    # 商品详细描述
    details = MDTextField(verbose_name=_('商品的详细描述'),
                          help_text=_('Please describe your product in detail'),
                          )

    # 商品简单描述
    intro = models.TextField(verbose_name=_('商品的简要描述'),
                             help_text=_('A briefly describe'),
                             max_length=100,
                             )

    # 商品种类
    commodity_choice = (
        ('衣服', '衣服'),
        ('裤子', '裤子'),
        ('鞋子', '鞋子'),
        ('电子设备', '电子设备'),
        ('化妆品', '化妆品'),
        ('食品', '食品'),
        ('帽子', '帽子'),
        ('袜子', '袜子'),
        ('游戏', '游戏'),
        ('户外装备', '户外装备'),
        ('手表', '手表'),
        ('饰品', '饰品'),
        ('生活用品', '生活用品'),
        ('家居', '家居'),
        ('其他', '其他')
    )
    category = models.CharField(verbose_name=_('商品类别'),
                                help_text=_('Please select the type of goods'),
                                max_length=10,
                                choices=commodity_choice,
                                )
    # 上架状态
    shelve_state = (
        ('0', '下架'),
        ('1', '上架'),
    )
    status = models.CharField(verbose_name=_('上架状态'),
                              help_text=_('请选择商品是否上架'),
                              max_length=10,
                              choices=shelve_state,
                              )

    # 上架时间

    onshelve_time = models.DateTimeField(auto_now=True,
                                         verbose_name=_('上架时间'),
                                         )

    # 下架时间

    unshelve_time = models.DateTimeField(auto_now=True,
                                         verbose_name=_('下架时间'))

    # 是否存在优惠,打几折

    discounts = models.DecimalField(verbose_name=_('是否优惠'),
                                    max_digits=2,
                                    decimal_places=1,
                                    default=1.0,
                                    help_text=_('是否在节假日打折,打几折？'))
    # 销售量
    sell_counts = models.PositiveIntegerField(verbose_name=_('销售量'),
                                              default=0, )

    # 运费
    freight = models.PositiveIntegerField(verbose_name=_('运费'),
                                          default=0,
                                          help_text=_('该商品是否有运费'))

    # 商品主图片
    image = models.ImageField(verbose_name=_('图片'), upload_to='commodity_head', help_text=_('商品主图片'), null=True)

    def images(self):
        # 显示图片而不是文件名
        if not self.image:
            return '无'
        else:
            return format_html("<img src='{}' style='width:100px;height:100px;'>",
                               self.image.url,
                               self.image)

    # 优惠活动说明
    discounts_intro = models.TextField(
        verbose_name=_('优惠活动说明'),
        max_length=100,
        help_text=_('请对优惠活动进行说明'),
        default=_('该店铺目前暂无优惠活动'),
    )

    # 库存
    stock = models.IntegerField(verbose_name=_('库存'),
                                help_text=_('请修改您的库存量'),
                                default=5000)

    commodity_ = Manager()

    class Meta:
        db_table = 'Commodity'
        verbose_name = _('商品表')
        verbose_name_plural = _('商品表')

    def __str__(self):
        return '商品'

    def colored_status(self):
        """替换状态颜色"""
        color_code = ''
        if self.status == 'Unshelve':
            color_code = '#E92B34'
        elif self.status == 'Onshelve':
            color_code = '#5DECA5'
        # display_name = self.get_status_display()
        return format_html(
            '<span style="color:{};font-size:16px;font-weight:bolder;">{}</span>',
            color_code,
            self.status,
        )

    colored_status.short_description = '上架状态'


class Goodsby(models.Model):
    """商品轮播表"""

    # 商品名
    commodity_name = models.CharField(verbose_name=_('商品名称'),
                                      help_text=_('Please enter the name of the product'),
                                      max_length=100,
                                      )
    # 图片
    picture = models.ImageField(verbose_name=_('轮播图片'),
                                upload_to='carousel')

    # 商品链接
    url = models.URLField(verbose_name=_('商品链接'), max_length=20)

    class Meta:
        db_table = "Carousel_index"
        verbose_name = _('首页轮播商品')
        verbose_name_plural = _('首页轮播商品')

    def __str__(self):
        return self.commodity_name


class GoodsType(models.Model):
    """商品类型表"""
    category = models.CharField(verbose_name=_('种类名称'), max_length=20)
    logo = models.CharField(verbose_name=_('logo标识'), max_length=20)
    image = models.ImageField(verbose_name=_('图片'), upload_to='category')

    class Meta:
        db_table = "Commodity_category"
        verbose_name = _('商品类型')
        verbose_name_plural = _('商品类型')


class Promotion(models.Model):
    """首页促销表"""
    # 促销商品名
    commodity_name = models.CharField(verbose_name=_('商品名称'), max_length=20)
    # 促销链接
    url = models.URLField(verbose_name=_('活动链接'), max_length=20)
    # 图片
    picture = models.ImageField(verbose_name=_('促销商品图片'),
                                upload_to='promotion')
    # 活动起始时间
    start_time = models.DateTimeField(verbose_name=_('活动持续时间'),
                                      auto_now_add=True)
    # 活动结束时间
    end_time = models.DateTimeField(verbose_name=_('活动结束时间'),
                                    auto_now_add=True)

    class Meta:
        db_table = "Promotion_commodity"
        verbose_name = _('促销商品')
        verbose_name_plural = _('促销商品')
