# -*- coding: utf-8 -*-
# @Time  : 2020/11/10 上午12:08
# @Author : 司云中
# @File : seckill_redis.py
# @Software: Pycharm
import math
import time
import uuid

from Emall.base_redis import BaseRedis


class Seckill(BaseRedis):
    """秒杀操作"""

    def __init__(self, db, redis):
        super().__init__(db, redis)

    def acquire_lock_with_timeout(self, conn, lock_name, acquire_timeout=3, lock_timeout=3, **kwargs):
        """
        基于 Redis 实现的单点分布式锁

        :param conn: Redis 连接
        :param lock_name: 锁的名称
        :param acquire_timeout: 获取锁的超时时间，默认 3 秒
        :param lock_timeout: 锁的超时时间，默认 2 秒
        :return:
        """

        identifier = str(uuid.uuid4())
        lock_name = f'redis-lock:{lock_name}'
        lock_timeout = int(math.ceil(lock_timeout))

        end = time.time() + acquire_timeout
        commodity_id = kwargs.pop('pk')  # 弹出商品id
        key = self.key('rob-lock',commodity_id)

        while time.time() < end:
            # 如果不存在这个锁则加锁并设置过期时间，避免死锁

            if conn.set(lock_name, identifier, ex=lock_timeout, nx=True):  # 如果拿到锁
                conn.decr(key)  # 减去一
                return identifier  # 返回唯一标识

        return False

    def release_lock(conn, lock_name, identifier):
        """
        释放锁

        :param conn: Redis 连接
        :param lockname: 锁的名称
        :param identifier: 锁的标识
        :return:
        """
        # python中redis事务是通过pipeline的封装实现的
        with conn.pipeline() as pipe:
            lock_name = 'lock:' + lock_name

            while True:
                try:
                    # watch 锁,监听该锁, multi 后如果该 key 被其他客户端改变, 事务操作会抛出 WatchError 异常,使得当前客户端不会误删了别人的锁
                    pipe.watch(lock_name)
                    ident = pipe.get(lock_name)
                    if ident and ident.decode('utf-8') == identifier:
                        # 事务开始

                        pipe.multi()
                        pipe.delete(lock_name)
                        pipe.execute()
                        return True

                    pipe.unwatch()
                    break
                except WatchError:
                    pass
            return False
