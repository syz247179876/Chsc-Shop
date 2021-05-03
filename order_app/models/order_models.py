from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from shop_app.models.commodity_models import Commodity, Sku
from user_app.models import Address
from voucher_app.models.voucher_models import Voucher

User = get_user_model()


class OrderBasic(models.Model):
    """订单基本信息"""

    # 订单号
    order_id = models.CharField(
        max_length=50, verbose_name=_("订单号"))

    # 用户，一个用户多个收货地址
    user = models.ForeignKey(User, verbose_name=_('用户名'),
                             max_length=50,
                             related_name='order_basic',
                             on_delete=models.CASCADE,
                             )

    # 收货地址,后期改成下拉列表的形式
    address = models.ForeignKey(Address, verbose_name=_('收货人'),
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='order_basic'
                                )

    # 红包优惠卷
    voucher = models.ForeignKey(Voucher, verbose_name=_('红包优惠卷'),
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='order_basic'
                                )

    # 支付方式
    payment_choice = (
        ('0', '尚未付款'),
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
    total_counts = models.PositiveIntegerField(verbose_name=_('商品总数'),
                                               default=1,
                                               validators=[
                                                   MaxValueValidator(10000,
                                                                     message=_('订单中商品总数不超过10000件')),
                                                   MinValueValidator(0, message=_('商品价格必须为正数'))])
    # 商品总价钱
    total_price = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name=_('商品总价格'),
                                      help_text=_('商品原价*商品数量'),
                                      validators=[MaxValueValidator(9999999.99,
                                                                    message=_('商品的总价格不能超过9999999.99人民币')),
                                                  MinValueValidator(0, message=_('商品价格必须为正数'))])
    # 商品优惠总价格
    favourable_price = models.DecimalField(max_digits=9, decimal_places=2,
                                           verbose_name=_('商品优惠总价格'),
                                           help_text=_('商品原价*折扣*商品数量'),
                                           validators=[MaxValueValidator(9999999.99,
                                                                         message=_('商品的总价格不能超过9999999.99人民币')),
                                                       MinValueValidator(0, message=_('商品价格必须为正数'))])

    # 商品真实总价格,优惠价格再减去使用的红包礼卷
    true_price = models.DecimalField(max_digits=9, decimal_places=2,
                                     verbose_name=_('商品真实的总价格'),
                                     help_text=_('商品原价*折扣*商品数量-红包礼卷'),
                                     validators=[MaxValueValidator(9999999.99,
                                                                   message=_('商品的总价格不能超过9999999.99人民币')),
                                                 MinValueValidator(0, message=_('商品价格必须为正数'))])

    # 产生订单日期
    generate_time = models.DateTimeField(verbose_name=_('生成订单时间'), auto_now_add=True)

    # 审核订单完毕日期
    check_time = models.DateTimeField(verbose_name=_('审核完毕订单时间'), auto_now=True)

    # 交易编号,支付包会返回的一个编号
    trade_number = models.CharField(verbose_name=_('交易编号'), max_length=128, null=True)

    # 订单状态
    status_choice = (
        ("1", '待付款'),  # 用户提交订单，尚未付款，此时会锁定库存
        ("2", '待发货'),  # 用户付款后，等待商家接单前
        ("3", '待收货'),  # 用户付款后，等待收获
        ("4", '交易成功'),  # 用户确认收货之后，订单完成交易
        ("5", '已取消'),  # 付款前取消订单
        ("6", '售后中'),  # 商家发货或付款后，用户取消订单
        ("7", '交易关闭'),  # 取消订单或售后结束或退货成功都转移到交易关闭
        ("8", '正在退货'),  # 用户选择退货，移至此
        ("9", '退款成功'),  # 用户退货成功后，移至此
    )

    status = models.CharField(verbose_name=_('订单状态'),
                              max_length=1,
                              choices=status_choice,
                              default="1",
                              )

    # 是否审核（同意接单）
    is_checked = models.BooleanField(verbose_name=_('是否审核'), default=False)

    # 是否可以评论
    is_remark = models.BooleanField(verbose_name=_('是否可以评论'), default=False)

    # 用户删除订单状态，假删除
    delete_consumer = models.BooleanField(verbose_name=_('消费者是否删除订单'), default=False)

    # 商家删除订单状态，假删除
    delete_seller = models.BooleanField(verbose_name=_('商家是否删除订单'), default=False)

    # 订单提交有效时间
    efficient_time = models.DateTimeField(verbose_name=_('订单过期时间'), auto_now=True)

    order_basic_ = Manager()

    class Meta:
        db_table = 'order_basic'
        verbose_name = _('订单基本表')
        verbose_name_plural = _('订单基本表')

    def __str__(self):
        return '订单号:{}'.format(self.order_id)


class OrderDetail(models.Model):
    """订单商品表，详情订单，针对某一种商品"""

    user = models.ForeignKey(User, verbose_name=_('商家'), related_name='order_details', on_delete=models.CASCADE)

    # 商品，显示商品下架
    commodity = models.ForeignKey(Commodity,
                                  verbose_name=_('商品'),
                                  related_name='order_details',
                                  on_delete=models.SET_NULL,
                                  null=True
                                  )

    # 属于哪一个订单，订单号
    order_basic = models.ForeignKey(OrderBasic, verbose_name=_('订单号'),
                                    help_text=_('属于哪个一个订单'),
                                    on_delete=models.CASCADE,
                                    related_name='order_details',
                                    )

    # 某种商品的数量
    counts = models.PositiveIntegerField(
        verbose_name=_('商品总数'),
        default=1,
        validators=[
            MaxValueValidator(10000, message=_('订单中商品总数不超过10000件'))]
    )

    # 商品下的sku
    sku = models.ForeignKey(Sku, verbose_name=_('商品的sku'), on_delete=True, related_name="order_detail")

    # 用户删除订单状态，假删除
    delete_consumer = models.BooleanField(verbose_name=_('消费者是否删除订单'), default=False)

    # 商家删除订单状态，假删除
    delete_seller = models.BooleanField(verbose_name=_('商家是否删除订单'), default=False)

    order_detail_ = Manager()

    class Meta:
        db_table = 'OrderDetail'
        verbose_name = _('订单商品详情表')
        verbose_name_plural = _('订单商品详情表')


class Logistic(models.Model):
    """物流表"""
    # 订单
    order_basic = models.ForeignKey(OrderBasic,
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

    # 买家是否签收
    signed = models.BooleanField(verbose_name=_('是否签收'),
                                 default=False,
                                 )

    class Meta:
        db_table = 'Logistic'
        verbose_name = _('物流表')
        verbose_name_plural = _('物流表')
