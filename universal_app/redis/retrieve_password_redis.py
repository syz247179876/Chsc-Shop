# -*- coding: utf-8 -*-
# @Time  : 2020/11/1 上午12:42
# @Author : 司云中
# @File : retrieve_password_redis.py
# @Software: Pycharm
from Emall.base_redis import BaseRedis, manager_redis


class RetrievePasswordRedis(BaseRedis):
    """忘记密码/找回密码Redis操作"""


    def check_code_retrieve(self, key):
        """校验唯一凭证并返回凭证值后删除凭证"""
        try:

            with manager_redis(self.db) as redis:
                pipe = redis.pipeline()
                identity = pipe.get(key)
                pipe.delete(key)
                pipe.execute()
        except Exception as e:
            return False, None
        if identity:
            # 存在
            return True, identity






