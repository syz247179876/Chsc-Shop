from django.db import models

# Create your models here.
from django.db.models import Manager
from Order_app.models.order_models import Order_basic
from django.utils.translation import gettext_lazy as _

class PayInformation(models.Model):
    """
    支付信息
    """

    # 一对一订单基本表
    order_basic = models.OneToOneField(Order_basic,on_delete=True, verbose_name=_('订单基本表'), related_name='PayInformation')

    # 交易号
    trade_id = models.CharField(
        max_length=100, verbose_name=_("支付流水号"))

    # 交易创建时间，一旦创建不能修改
    generate_time = models.DateTimeField(verbose_name=_('完成交易'), auto_now_add=True)

    payment_ = Manager()

    class Meta:
        db_table = 'PayInformation'
        verbose_name = '支付信息'
        verbose_name_plural = verbose_name





