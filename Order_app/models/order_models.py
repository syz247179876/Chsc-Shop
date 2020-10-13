from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Manager
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from Shop_app.models.commodity_models import Commodity
from User_app.models.user_models import Address


class Order_basic(models.Model):
    """订单基本信息"""

    # 订单号
    orderId = models.CharField(
        max_length=100, verbose_name=_("支付流水号"))

    # 用户，一个用户多个收货地址
    consumer = models.ForeignKey(User, verbose_name=_('用户名'),
                                 max_length=50,
                                 related_name='order_basic',
                                 on_delete=models.CASCADE,
                                 )

    # 收货地址,后期改成下拉列表的形式
    region = models.ForeignKey(Address, verbose_name=_('收货人'),
                               on_delete=models.CASCADE,
                               related_name='order_basic'
                               )
    # 支付方式
    payment_choice = (
        ('1', '货到付款'),
        ('2', '微信支付'),
        ('3', '支付宝'),
        ('4', '银联支付')
    )
    payment = models.CharField(verbose_name=_('支付方式'),
                               choices=payment_choice,
                               max_length=1,
                               )

    # 商品总数
    commodity_total_counts = models.PositiveIntegerField(verbose_name=_('商品总数'),
                                                         default=1,
                                                         validators=[
                                                             MaxValueValidator(10000,
                                                                               message=_('订单中商品总数不超过10000件')), ])
    # 商品总价钱
    total_price = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name=_('商品总价格'),
                                      validators=[MaxValueValidator(99999999.99,
                                                                    message=_('商品的总价格不能超过999999.99人民币')), ],
                                      null=True)

    # 产生订单日期
    generate_time = models.DateTimeField(verbose_name=_('生成订单时间'), auto_now_add=True)

    # 审核订单完毕日期
    check_time = models.DateTimeField(verbose_name=_('审核完毕订单时间'), auto_now=True)

    # 交易编号,支付包会返回的一个编号
    trade_number = models.CharField(verbose_name=_('交易编号'), max_length=128, null=True)

    # 订单状态
    status_choice = (
        ("1", '代付款'),  # 用户提交订单，尚未付款，此时会锁定库存
        ("2", '代发货'),  # 用户付款后，等待商家接单前
        ("3", '代收货'),  # 用户付款后，等待收获
        ("4", '交易成功'),  # 用户确认收货之后，订单完成交易
        ("5", '已取消'),  # 付款前取消订单
        ("6", '售后中'),  # 商家发货或付款后，用户取消订单
        ("7", '交易关闭'),  # 取消订单或售后结束或退货成功都转移到交易关闭
        ("8", '正在退货'),  # 用户选择退货，移至此
        ("9", '退款成功'),  # 用户选择退货，移至此
    )

    status = models.CharField(verbose_name=_('订单状态'),
                              max_length=1,
                              choices=status_choice,
                              default=1,
                              )

    # 是否审核（同意接单）
    checked = models.BooleanField(verbose_name=_('是否审核'), default=False)

    # 是否可以评论
    remarked = models.BooleanField(verbose_name=_('是否可以评论'), default=False)

    # 用户删除订单状态，假删除
    delete_consumer = models.BooleanField(verbose_name=_('消费者是否删除订单'), default=False)

    # 商家删除订单状态，假删除
    delete_shopper = models.BooleanField(verbose_name=_('商家是否删除订单'), default=False)

    # 订单提交有效时间
    efficient_time = models.DateTimeField(verbose_name=_('订单过期时间'), null=True, auto_now=True)

    order_basic_ = Manager()

    class Meta:
        db_table = 'Order_basic'
        verbose_name = _('订单信息表')
        verbose_name_plural = _('订单信息表')

    def __str__(self):
        return '订单号:{}'.format(self.orderId)


class Order_details(models.Model):
    """子订单商品表，详情订单，针对某一种商品"""

    # 对应的店家
    belong_shopper = models.ForeignKey(User,
                                       verbose_name=_('商家'),
                                       help_text=_('该商品所对应的商家'),
                                       on_delete=models.CASCADE,
                                       related_name='order_details',
                                       )
    # 商品，商品下架，订单详情销毁
    commodity = models.OneToOneField(Commodity,
                                     verbose_name=_('商品'),
                                     related_name='order_details',
                                     on_delete=models.CASCADE,
                                     )

    # 属于哪一个订单，订单号
    order_basic = models.ForeignKey(Order_basic, verbose_name=_('订单号'),
                                    help_text=_('属于哪个一个订单'),
                                    on_delete=models.CASCADE,
                                    related_name='order_details',
                                    )
    # 商品的价格,可以是折后价
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('商品价格'),
                                validators=[MaxValueValidator(999999.99, message=_('商品的最高单价不能超过999999.99人民币')),
                                            MinValueValidator(0, message=_('商品价格必须为正数'))])

    # 某种商品的数量
    commodity_counts = models.PositiveIntegerField(
        verbose_name=_('商品总数'),
        default=1,
        validators=[
            MaxValueValidator(10000, message=_('订单中商品总数不超过10000件'))]
    )

    # 该商品标签（尺寸，颜色，规格等）
    label = models.CharField(max_length=25, default='无')

    order_details_ = Manager()

    class Meta:
        db_table = 'Order_details'
        verbose_name = _('订单商品详情表')
        verbose_name_plural = _('订单商品详情表')


class Logistic(models.Model):
    """物流表"""
    # 订单
    order_basic = models.ForeignKey(Order_basic,
                                    verbose_name=_('订单'),
                                    related_name='logistic',
                                    on_delete=models.CASCADE)

    # 发货状态
    shipping_status_choice = (
        (1, '未发货'),
        (2, '已发货')
    )
    shipping_status = models.SmallIntegerField(verbose_name=_('发货状态'),
                                               default=1,
                                               choices=shipping_status_choice,
                                               )

    def shipping_status_color(self):
        """重绘发货状态颜色"""
        color_code = ''
        if self.shipping_status == 1:
            color_code = '#5DECA5',
        elif self.shipping_status == 2:
            color_code = '#E92B34'
            # display_name = self.get_check_status_display()
        return format_html(
            '<span style="color:{}";>{}</span>',
            color_code,
            self.get_shipping_status_display(),
        )

    shipping_status_color.short_description = '发货状态'
    # 买家是否签收
    signed = models.BooleanField(verbose_name=_('是否签收'),
                                 default=False,
                                 )

    class Meta:
        db_table = 'Logistic'
        verbose_name = _('物流表')
        verbose_name_plural = _('物流表')
