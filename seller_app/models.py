from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from universal_app.models import Role

User = get_user_model()

class Store(models.Model):

    # 店铺名
    name = models.CharField(verbose_name=_('店铺名'), max_length=30, unique=True)

    # 店铺简介
    intro = models.CharField(verbose_name=_('店铺简介'), max_length=128)

    TYPE = (
        ('1', '个人店(免费入驻)'),
        ('2', '企业店')
    )
    # 开店类型
    type = models.CharField(choices=TYPE, verbose_name=_('开店类型'), default='1', max_length=1)

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
    integral = models.PositiveIntegerField(verbose_name=_('店铺积分'), default=0)

    # 是否通过审核
    is_checked = models.BooleanField(default=True, verbose_name=_('是否通过管理员的审核'))

    # 店铺logo
    logo = models.CharField(max_length=256,verbose_name=_('店铺logo'))

    # 商品描述分数
    description_score = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_('商品描述分数'), default=5.0)

    # 卖家服务分数
    service_score = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_('卖家服务分数'), default=5.0)

    # 物流服务分数
    logistics_score = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_('物流服务分数'), default=5.0)

    objects = Manager()

    class Meta:
        db_table = 'store'

class Seller(models.Model):
    """商家表"""
    user = models.OneToOneField(to=User, verbose_name=_('商家'), related_name='seller', on_delete=models.CASCADE)

    store = models.OneToOneField(to=Store, verbose_name=_('店铺'), related_name='seller', on_delete=models.CASCADE)

    safety = models.PositiveIntegerField(
        _('安全分数'),
        help_text=_('您的信息安全分数'),
        default=60,
    )

    integral = models.PositiveIntegerField(
        _('积分值'),
        default=0
    )

    role = models.ForeignKey(to=Role, on_delete=models.SET_NULL, related_name='seller', null=True)

    objects = Manager()
    class Meta:
        db_table = 'seller'