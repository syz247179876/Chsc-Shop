from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from user_app.models import Consumer, User
from shop_app.models.commodity_models import Commodity


# Create your models here.

class Remark(models.Model):
    """
    评论表
    商家不能修改评论表
    """

    # 商家
    shopper = models.ForeignKey(User,
                                verbose_name=_('商家'),
                                help_text=_('评论的商家'),
                                on_delete=models.CASCADE,
                                related_name='remark_shopper',
                                )
    # 用户
    consumer = models.ForeignKey(User,
                                 verbose_name=_('消费者'),
                                 help_text=_('您所评分的商家'),
                                 on_delete=models.CASCADE,
                                 related_name='remark_consumer',
                                 )
    # 商品,一个评价只能对应一个商品，一个商品出现在多个用户的评价中
    commodity = models.ForeignKey(Commodity,
                                  verbose_name=_('商品'),
                                  help_text=_('您所评分的商品'),
                                  on_delete=models.CASCADE,
                                  related_name='remark',
                                  )

    # 评分
    grade_choice = (
        (1, '一星好评'),
        (2, '二星好评'),
        (3, '三星好评'),
        (4, '四星好评'),
        (5, '五星好评'),
    )
    grade = models.SmallIntegerField(verbose_name=_('评分'), help_text=_('Please rate the goods'), choices=grade_choice)

    # 评论内容
    reward_content = models.TextField(verbose_name=_('评论内容'),
                                      help_text=_('Please enter a comment'),
                                      max_length=128)

    # 评论时间
    reward_time = models.DateTimeField(auto_now_add=True, verbose_name=_('评论时间'))

    # 判断用户是否已经评论
    is_remark = models.BooleanField(default=True)

    # 点赞个数
    praise = models.PositiveIntegerField(verbose_name=_('点赞数'), default=0)

    # 差评个数
    against = models.PositiveIntegerField(verbose_name=_('差评数'), default=0)

    # 是否已经点赞还是差评
    is_action = models.BooleanField(default=False)


    remark_ = Manager()

    class Meta:
        db_table = 'Remark'
        verbose_name = _('评论表')
        verbose_name_plural = _('评论表')


class Remark_reply(models.Model):
    """评论回复"""

    '''商家只能修改回复表'''

    # 回复内容
    reply_content = models.TextField(verbose_name=_('评论内容'), help_text=_('Please enter a comment'))

    # 回复时间
    reply_time = models.DateTimeField(auto_now_add=True, verbose_name=_('回复时间'))

    # 评论
    remark = models.ForeignKey(Remark,
                               verbose_name=_('评论'),
                               help_text=_('请填写对评论的回复'),
                               related_name='remark_reply',
                               on_delete=models.CASCADE,
                               )
    # 商家
    shopper = models.OneToOneField(User,
                                   verbose_name=_('商家'),
                                   help_text=_('商家'),
                                   related_name='remark_reply',
                                   on_delete=models.CASCADE
                                   )

    # 点赞个数
    praise = models.PositiveIntegerField(verbose_name=_('点赞数'), default=0)

    # 差评个数
    against = models.PositiveIntegerField(verbose_name=_('差评数'), default=0)

    # 是否已经点赞还是差评
    is_action = models.BooleanField(default=False)

    class Meta:
        db_table = 'Remark_reply'
        verbose_name = _('评论回复表')
        verbose_name_plural = _('评论回复表')
