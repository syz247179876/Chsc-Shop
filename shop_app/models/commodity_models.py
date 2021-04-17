import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from seller_app.models import Store
from shop_app.utils.validators import *

User = get_user_model()


class CategoryManager(Manager):

    def first_create(self, **data):
        """创建商品总类别"""
        self.create(pre=None, has_prev=False, has_next=True, **data)


class CommodityCategory(models.Model):
    """商品类别表"""

    # 种类名
    name = models.CharField(verbose_name=_('种类名'), max_length=50, unique=True)

    # 添加时间
    add_time = models.DateTimeField(verbose_name=_('添加种类时间'), auto_now_add=True)

    # 种类简要介绍
    intro = models.CharField(verbose_name=_('简要介绍'), max_length=100)

    # 缩略图
    thumbnail = models.CharField(verbose_name=_('列表缩略图'), max_length=50, null=True)

    # 分数值排序
    sort = models.PositiveIntegerField(verbose_name=_('商品分数值'), help_text=_('用于商品间的排序'), default=0)

    # 上一级分类的id
    pre = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    # 是否有前驱结点
    has_prev = models.BooleanField(verbose_name=_('是否有前驱'), default=False)

    # 是否有后继结点
    has_next = models.BooleanField(verbose_name=_('是否有后继'), default=False)

    objects = CategoryManager()

    class Meta:
        db_table = 'commodity_category'
        ordering = ('add_time',)
        verbose_name = _('分类表')
        verbose_name_plural = _('分类表')


class CommodityGroup(models.Model):
    """商品分组表"""

    name = models.CharField(verbose_name=_('分组名称'), max_length=15)
    status = models.BooleanField(verbose_name=_('分组状态'))

    objects = Manager()

    class Meta:
        db_table = 'commodity_groups'
        ordering = ('status',)


class Freight(models.Model):
    """商品运费表"""
    name = models.CharField(verbose_name=_('运费模板名称'), max_length=15)

    # 是否包邮
    is_free = models.BooleanField(verbose_name=_('是否包邮'))

    # 收费方式
    CHARGE_TYPE = (
        ('0', '按重量'),
        ('1', '按件数'),
        ('2', '按体积')
    )

    charge_type = models.CharField(max_length=1, choices=CHARGE_TYPE, verbose_name=_('收费方式'), null=True)

    objects = Manager()

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

    # 启用状态
    status = models.BooleanField(default=True, verbose_name=_('是否启用'))

    # 不同首件个数不同优惠幅度
    first_piece = models.PositiveIntegerField(verbose_name=_('首件数量'))

    # 多件商品后运费价格会变化
    continue_piece = models.PositiveIntegerField(verbose_name=_('续件数量'))

    # 首件对应的运费价格
    first_price = models.PositiveIntegerField(verbose_name=_('首件运费'))

    # 续件对应的运费价格
    continue_price = models.PositiveIntegerField(verbose_name=_('续件运费'))

    # 存储key-value格式的 城市编号：城市键值对格式的字符串
    city = models.TextField()

    objects = Manager()

    class Meta:
        db_table = "freight_item"


class Commodity(models.Model):
    """商品表"""

    # 商家
    user = models.ForeignKey(to=User, verbose_name=_('商家'), related_name='commodity', on_delete=models.CASCADE)

    # 店铺
    store = models.ForeignKey(to=Store, verbose_name=_('店铺'), related_name='commodity', on_delete=models.CASCADE)

    # 商品名称
    commodity_name = models.CharField(verbose_name=_('商品名称'),
                                      help_text=_('Please enter the name of the product'),
                                      max_length=25,
                                      validators=[CommodityValidator(), ]
                                      )
    # 商品价格,正整数
    price = models.DecimalField(verbose_name=_('价格'),
                                help_text=_('商品原价'),
                                max_digits=9, decimal_places=2,
                                validators=[MaxValueValidator(9999999.99,
                                                              message=_('商品的最高单价不能超过9999999.99人民币')),
                                            MinValueValidator(0, message=_('商品价格必须为正数'))]
                                )

    # 商品优惠价格
    favourable_price = models.DecimalField(verbose_name=_('优惠价格'),
                                           max_digits=9, decimal_places=2,
                                           help_text=_('优惠后的商品价格'),
                                           validators=[
                                               MaxValueValidator(9999999.99,
                                                                 message=_('商品的最高单价不能超过9999999.99人民币')),
                                               MinValueValidator(0, message=_('商品价格必须为正数'))]
                                           )

    # 商品详细描述
    details = models.TextField(verbose_name=_('商品的详细描述'),
                               help_text=_('商品详细描述'),
                               )

    # 商品简单描述
    intro = models.CharField(verbose_name=_('商品的简要描述'),
                             help_text=_('商品简单描述'),
                             max_length=80,
                             )

    # 商品分类
    category = models.ForeignKey(to=CommodityCategory, verbose_name=_('商品类别'), on_delete=models.CASCADE)

    # 商品分组,多对多
    group = models.ManyToManyField(to=CommodityGroup, verbose_name=_('商品分组'))

    # 商品上架状态
    status = models.BooleanField(verbose_name=_('上架状态'),
                                 help_text=_('请选择商品是否上架'),
                                 default=False
                                 )

    # 上架时间,自动设置
    onshelve_time = models.DateTimeField(auto_now=True,
                                         verbose_name=_('上架时间'))

    # 下架时间
    unshelve_time = models.DateTimeField(null=True,
                                         verbose_name=_('下架时间'))

    # 销售量
    sell_counts = models.PositiveIntegerField(verbose_name=_('销售量'),
                                              default=0, editable=False)

    # 运费模板, 在删除该运费模板时,若已被使用抛出ProtectedError异常
    freight = models.ForeignKey(to=Freight, verbose_name=_('运费模板id'),
                                help_text=_('该商品是否有运费'), on_delete=models.PROTECT)

    # 商品轮播主图片
    big_image = models.TextField(verbose_name=_('主图片'), help_text=_('商品轮播主图片'))

    # 商品小图片
    little_image = models.CharField(verbose_name=_('小图片'), help_text=_('商品小图片'), max_length=256)

    # 库存
    stock = models.PositiveIntegerField(verbose_name=_('库存'),
                                        help_text=_('请修改您的库存量'),
                                        default=0)

    # 分数值排序
    sort = models.PositiveIntegerField(verbose_name=_('商品分数值'), help_text=_('用于商品间的排序'), default=0)

    # 商品关键属性spu
    spu = models.TextField(verbose_name=_('商品spu'), null=True)

    commodity_ = Manager()

    class Meta:
        db_table = 'commodity'
        verbose_name = _('商品表')
        verbose_name_plural = _('商品表')

    def __str__(self):
        return 'commodity_name:{}'.format(self.commodity_name)


class Carousel(models.Model):
    """商品轮播表"""

    # 图片
    picture = models.CharField(verbose_name=_('轮播图片地址'), max_length=128)

    # 轮播图链接
    url = models.URLField(verbose_name=_('轮播图跳转链接'), max_length=128)

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

    objects = Manager()

    class Meta:
        db_table = "carousel"
        verbose_name = _('首页轮播商品')
        verbose_name_plural = _('首页轮播商品')
        ordering = ('sort',)


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

    class Meta:
        db_table = "seckill"
        verbose_name = _('秒杀商品')
        verbose_name_plural = _('秒杀商品')


class Sku(models.Model):
    """
    sku表

    对能够影响商品销量和库存的销售属性集合进行排列组合的迪卡尔积种类
    """

    # 关系为多对一,原因在于对sku中的关键属性进行排列组合,每一种情况都是一个sku,因此多个sku对应一个商品
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name=_('商品'), related_name='sku')

    # 库存
    stock = models.PositiveIntegerField(verbose_name=_('sku的库存'), default=0)

    # 原价
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('sku的价格'),
                                validators=[MaxValueValidator(999999.99, message=_('商品的最高单价不能超过999999.99人民币')),
                                            MinValueValidator(0, message=_('商品价格必须为正数'))])

    # 优惠价格
    favourable_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('sku的优惠价格'),
                                           validators=[
                                               MaxValueValidator(999999.99, message=_('商品的最高单价不能超过999999.99人民币')),
                                               MinValueValidator(0, message=_('商品价格必须为正数'))])

    # sku销售属性JSON字符串, 3.1使用允许使用JsonField字段
    properties = models.TextField()

    # 修改时间
    update_time = models.DateTimeField(auto_now=True)

    # sku的图片
    image = models.CharField(verbose_name=_('主图片'), help_text=_('sku主图片'), max_length=256, null=True)

    # sku名称
    name = models.CharField(verbose_name=_('sku名称'), max_length=50)

    # sku是否上下架
    status = models.BooleanField(verbose_name=_('sku状态'))

    class Meta:
        db_table = 'sku'


class SkuProps(models.Model):
    """
    Sku的规格属性表
    保存常用属性
    """

    # sku属性属于哪一个商品
    commodity = models.ForeignKey(Commodity, on_delete=True, verbose_name=_('商品'), related_name='commodity')

    name = models.CharField(verbose_name=_('sku属性名称'), max_length=20)

    objects = Manager()

    class Meta:
        db_table = 'sku_props'


class SkuValues(models.Model):
    """
    sku的规格属性值表
    保存常用属性值
    """

    prop = models.ForeignKey(to=SkuProps, on_delete=models.CASCADE, related_name='values')

    value = models.CharField(verbose_name=_('sku属性值'), max_length=20)

    objects = Manager()

    class Meta:
        db_table = 'sku_values'
