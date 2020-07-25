from django.db import models

# Create your models here.
from git_emall.e_mall.Order_app.models.order_models import Order


class Payment(models.Model):
    """
    支付信息
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, verbose_name='订单', related_name='payment')

    trade_id = models.CharField(
        max_length=100, verbose_name="支付流水号")

    # 交易创建时间，一旦创建不能修改
    generate_time = models.DateTimeField(verbose_name=_('生成订单时间'), auto_now_add=True)

    # 交易修改时间
    modify_time = models.DateTimeField(verbose_name=_('修改订单时间'), auto_now=True)


class Meta:
    db_table = 'payment'
    verbose_name = '支付信息'
    verbose_name_plural = verbose_name
