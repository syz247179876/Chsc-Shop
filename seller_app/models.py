from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager


class Seller(models.Model):

    User = get_user_model()
    user = models.OneToOneField(to=User, verbose_name=_('商家'), related_name='seller', on_delete=models.CASCADE)

    store = models.OneToOneField(to=User, verbose_name=_('店铺'), related_name='seller', on_delete=models.CASCADE,
                                 null=True)

    safety = models.PositiveIntegerField(
        _('安全分数'),
        help_text=_('您的信息安全分数'),
        default=60,
    )

    integral = models.PositiveIntegerField(
        _('积分值'),
        default=0
    )

    objects = Manager()
    class Meta:
        db_table = 'seller'


class Store(models.Model):

    # 店铺名
    name = models.CharField(verbose_name=_('店铺名'), max_length=30)

    # 店铺简介
    intro = models.CharField(verbose_name=_('店铺简介'), max_length=128)

    RANK_SORT = (
        (0, '先锋'),
        (1000, '中军'),
        (5000, '统帅'),
        (10000, '传奇'),
        (20000, '万古流芳'),
        (50000, '超凡入圣'),
        (100000, '冠绝一世')
    )

    # 店铺等级
    rank = models.CharField(verbose_name=_('店铺等级'), max_length=4, default='先锋')

    # 店铺积分
    integral = models.PositiveIntegerField(verbose_name=_('店铺积分'))

    objects = Manager()

    class Meta:
        db_table = 'store'

