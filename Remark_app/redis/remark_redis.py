# -*- coding: utf-8 -*-
# @Time  : 2020/8/30 下午5:52
# @Author : 司云中
# @File : remark_redis.py
# @Software: Pycharm
from Remark_app.models.remark_models import Remark
from Remark_app.serializers.attitude_action_serializers import AttitudeRemarkSerializer
from Remark_app.signals import praise_or_against_post, praise_or_against_cancel, remark_post, \
    remark_cancel, check_remark_action
from Remark_app.views.remark_api import RemarkOperation
from e_mall.base_redis import BaseRedis
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

class RemarkRedisOperation(BaseRedis):
    """评论Redis操作类"""

    def __init__(self, db):
        super().__init__(db)
        self.connect()

    def connect(self):
        """注册信号"""
        common_logger.info(3333)  # 这里怎么加载了2次？
        praise_or_against_post.connect(self.praise_or_against_post, sender=AttitudeRemarkSerializer)
        praise_or_against_cancel.connect(self.praise_or_against_cancel, sender=AttitudeRemarkSerializer)
        remark_post.connect(self.remark_post, sender=RemarkOperation)
        remark_cancel.connect(self.remark_cancel, sender=RemarkOperation)
        check_remark_action.connect(self.record_remark_action, sender=Remark)

    def record_remark_action(self, sender, pk, user, is_remark, is_action, **kwargs):
        """检查是否允许点赞/反对  还是  是否允许评论"""
        user_pk = user.pk
        key = None
        if is_remark:
            key = self.key('remark', 'commodity', pk)  # key: 'remark-1'
        elif is_action:
            key = self.key('remark', 'action', pk)
        return True if self.redis.getbit(key, user_pk) else False  # 如果偏移量对应的bit为1,则表示用户已经点赞/反对过，反之没有

    def praise_or_against_post(self, sender, pk, user, **kwargs):
        """点赞/反对"""
        user_pk = user.pk
        key = self.key('remark', 'action', pk)  # key: 'remark-1'
        self.redis.setbit(key, user_pk, 1)

    def praise_or_against_cancel(self, sender, pk, user, **kwargs):
        """取消点赞/反对"""
        key = self.key('remark', pk)  # key: 'remark-1'
        user_pk = user.pk
        self.redis.setbit(key, user_pk, 0)  # 取消点赞/反对，设置偏移量的bit为0

    def remark_post(self, sender, commodity_pk, user, **kwargs):
        """添加评论时回调"""
        key = self.key('remark', 'commodity', commodity_pk)  # key: 'remark-commodity-1'
        user_pk = user.pk
        self.redis.setbit(key, user_pk, 1)

    def remark_cancel(self, cancel, commodity_pk, user, **kwargs):
        """删除评论时回调"""
        key = self.key('remark', 'commodity', commodity_pk)     # key: 'remark-commodity-1'
        user_pk = user.pk
        self.redis.setbit(key, user_pk, 0)


remark_redis = RemarkRedisOperation.choice_redis_db('remark')


