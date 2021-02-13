import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Manager
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from shop_app.utils.validators import *


class CommodityCategory(models.Model):
    """商品类别表"""

    # 种类名
    name = models.CharField(verbose_name=_('种类名'), max_length=50)

    # 添加时间
    add_time = models.DateTimeField(verbose_name=_('添加种类时间'), auto_now=True)

    # 种类简要介绍
    intro = models.CharField(verbose_name=_('简要介绍'), max_length=100)

    # 缩略图
    thumbnail = models.CharField(verbose_name=_('列表缩略图'), max_length=50)

    # 分数值排序
    sort = models.PositiveIntegerField(verbose_name=_('商品分数值'), help_text=_('用于商品间的排序'))

    # 上一级分类的id
    pre_id = models.ForeignKey('self', on_delete=models.CASCADE)


    class Meta:
        db_table = 'commodity_category'
        ordering = ('add_time',)
        verbose_name = _('分类表')
        verbose_name_plural = _('分类表')


class CommodityGroup(models.Model):
    """商品分组表"""

    name = models.CharField(verbose_name=_('分组名称'), max_length=15)
    class Meta:
        db_table = '商品分组表'


class Freight(models.Model):
    """商品运费表"""
    name = models.CharField(verbose_name=_('运费模板名称'), max_length=15)

    # 是否包邮
    isFree = models.BooleanField(verbose_name=_('是否包邮'))

    # 收费方式
    CHARGE_TYPE = (
        ('0', '按重量'),
        ('1', '按件数'),
        ('2', '按体积')
    )

    chargeType = models.CharField(max_length=1, verbose_name=_('收费方式'), null=True)


    class Meta:
        db_table = 'freight'
        verbose_name = _('运费模板表')
        verbose_name_plural = _('运费模板表')


class FreightItem(models.Model):
    """
    运费项表
    可根据不同区域进行配置,每固定区域内为一个运费项
    """

    freight = models.ForeignKey(to=Freight, verbose_name=_('运费id'), on_delete=models.CASCADE)

    # 不同首件个数不同优惠幅度
    first_piece = models.PositiveIntegerField(verbose_name=_('首件数量'))

    # 多件商品后运费价格会变化
    continue_piece = models.PositiveIntegerField(verbose_name=_('续件数量'))

    # 首件对应的运费价格
    first_price = models.PositiveIntegerField(verbose_name=_('首件运费'))

    # 续件对应的运费价格
    continue_price = models.PositiveIntegerField(verbose_name=_('续件运费'))

    class Meta:
        db_table = "freight_item"


class FreightItemCity(models.Model):
    """运费项城市表"""

    freight_item = models.ForeignKey(to=FreightItem, on_delete=models.CASCADE, verbose_name=_('运费项id'))

    freight = models.ForeignKey(to=Freight, on_delete=models.CASCADE, verbose_name=_('运费表id'))

    city = models.CharField(max_length=20, verbose_name=_('城市id'))



class Commodity(models.Model):
    """商品表"""

    # 商品名称
    commodity_name = models.CharField(verbose_name=_('商品名称'),
                                      help_text=_('Please enter the name of the product'),
                                      max_length=25,
                                      validators=[CommodityValidator(), ]
                                      )
    # 商品价格,正整数
    price = models.PositiveIntegerField(verbose_name=_('价格'),
                                        help_text=_('商品原价'),
                                        validators=[MaxValueValidator(9999999, message=_('商品最高价格不能高于9999999'))]
                                        )

    # 商品优惠价格
    favourable_price = models.PositiveIntegerField(verbose_name=_('优惠价格'),
                                                   help_text=_('优惠后的商品价格'),
                                                   validators=[
                                                       MaxValueValidator(9999999, message=_('商品最高价格不能高于9999999'))]
                                                   )

    # 商品详细描述
    details = models.TextField(verbose_name=_('商品的详细描述'),
                               help_text=_('商品详细描述'),
                               )

    # 商品简单描述
    intro = models.TextField(verbose_name=_('商品的简要描述'),
                             help_text=_('商品简单描述'),
                             max_length=80,
                             )

    # 商品分类
    category = models.ForeignKey(to=CommodityCategory, verbose_name=_('商品类别'), on_delete=models.SET_NULL , null=True)

    # 商品分组,多对多
    group = models.ManyToManyField(to=CommodityGroup, verbose_name=_('商品分组'))

    # 商品上架状态
    status = models.BooleanField(verbose_name=_('上架状态'),
                                 help_text=_('请选择商品是否上架'),
                                 default=False
                                 )

    # 上架时间,自动设置
    onshelve_time = models.DateTimeField(auto_now=True,
                                         verbose_name=_('上架时间'),
                                         )

    # 下架时间
    unshelve_time = models.DateTimeField(default=datetime.timezone,
                                         null=True,
                                         verbose_name=_('下架时间'))

    # 销售量
    sell_counts = models.PositiveIntegerField(verbose_name=_('销售量'),
                                              default=0, )

    # 运费模板, 在删除该运费模板时,若已被使用抛出ProtectedError异常
    freight = models.ForeignKey(to=Freight, verbose_name=_('运费模板id'),
                                          help_text=_('该商品是否有运费'), on_delete=models.PROTECT)

    # 商品主图片
    big_image = models.CharField(verbose_name=_('主图片'), help_text=_('商品主图片'), max_length=256)

    # 商品小图片
    little_image = models.CharField(verbose_name=_('小图片'), help_text=_('商品小图片'), max_length=256)

    # 库存
    stock = models.PositiveIntegerField(verbose_name=_('库存'),
                                        help_text=_('请修改您的库存量'),
                                        default=0)

    # 分数值排序
    sort = models.PositiveIntegerField(verbose_name=_('商品分数值'), help_text=_('用于商品间的排序'), default=0)

    commodity_ = Manager()

    class Meta:
        db_table = 'Commodity'
        verbose_name = _('商品表')
        verbose_name_plural = _('商品表')

    def __str__(self):
        return 'commodity_name:{}'.format(self.commodity_name)

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


class Carousel(models.Model):
    """商品轮播表"""

    # 图片
    picture = models.CharField(verbose_name=_('轮播图片地址'), max_length=128)

    # 轮播图链接
    url = models.URLField(verbose_name=_('轮播图链接'), max_length=20)

    # 排序
    sort = models.IntegerField(verbose_name=_('顺序'), default=0)

    TYPE = (
        ('1', '单个商品'),
        ('2', '商品系列'),
        ('3', '活动'),
        ('4', '店铺')
    )

    type = models.CharField(verbose_name=_('轮播图内容类型'), choices=TYPE, default='1', max_length=1)

    # 添加时间
    add_time = models.DateTimeField(auto_now=True)

    carousel_ = Manager()

    class Meta:
        db_table = "Carousel"
        verbose_name = _('首页轮播商品')
        verbose_name_plural = _('首页轮播商品')
        ordering = ('sort',)


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


class SeckKill(models.Model):
    """存放用于秒杀的商品表"""

    # 秒杀的商品映射
    seck_commodity = models.OneToOneField(Commodity, on_delete=True)

    # 秒杀开始时间
    start_time = models.DateTimeField(auto_now=True)

    # 秒杀结束时间
    end_time = models.DateTimeField(auto_now=True)

    # 是否过期
    is_expired = models.BooleanField(default=True)

    seck_kill_ = Manager()

    class Meta:
        db_table = "SeckKill"
        verbose_name = _('秒杀商品')
        verbose_name_plural = _('秒杀商品')


class Sku(models.Model):
    """
    sku表

    对能够影响商品销量和库存的关键属性集合进行排列组合的迪卡尔积种类
    """

    # 关系为多对一,原因在于对sku中的关键属性进行排列组合,每一种情况都是一个sku,因此多个sku对应一个商品
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name=_('商品'), related_name='sku')

    stock = models.PositiveIntegerField(verbose_name=_('sku的库存'), default=0)

    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('sku的价格'),
                                validators=[MaxValueValidator(999999.99, message=_('商品的最高单价不能超过999999.99人民币')),
                                            MinValueValidator(0, message=_('商品价格必须为正数'))])

    # sku分类, 3.1使用允许使用JsonField字段
    category = models.TextField()


class SkuProps(models.Model):
    """
    Sku的规格
    """
    pass
