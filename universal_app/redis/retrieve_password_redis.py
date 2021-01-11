# -*- coding: utf-8 -*-
# @Time  : 2020/11/1 上午12:42
# @Author : 司云中
# @File : retrieve_password_redis.py
# @Software: Pycharm
from Emall.base_redis import BaseRedis, manage_redis


class RetrievePasswordRedis(BaseRedis):
    """忘记密码/找回密码Redis操作"""

    def check_code_retrieve(self, key):
        """校验唯一凭证并返回凭证值后删除凭证"""
        try:

            with manage_redis(self.db) as redis:
                identity = redis.get(key)
                if identity:
                    # 存在
                    redis.delete(key)
                    return True, identity
        except Exception:
            return False, None
