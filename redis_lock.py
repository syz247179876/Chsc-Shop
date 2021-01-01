# # -*- coding: utf-8 -*-
# # @Time  : 2020/11/9 下午9:00
# # @Author : 司云中
# # @File : redis_lock.py
# # @Software: Pycharm
#
#
# import uuid
# import math
# import time
# from threading import Thread
#
# import redis
# from redis import WatchError
#
# count=50
#
# def acquire_lock_with_timeout(conn, lock_name, acquire_timeout=4, lock_timeout=2):
#     """
#     基于 Redis 实现的分布式锁
#
#     :param conn: Redis 连接
#     :param lock_name: 锁的名称
#     :param acquire_timeout: 获取锁的超时时间，默认 3 秒
#     :param lock_timeout: 锁的超时时间，默认 2 秒
#     :return:
#     """
#
#     identifier = str(uuid.uuid4())
#     lockname = f'lock:{lock_name}'
#     lock_timeout = int(math.ceil(lock_timeout))
#
#     end = time.time() + acquire_timeout
#
#     while time.time() < end:
#         # 如果不存在这个锁则加锁并设置过期时间，避免死锁
#         if conn.set(lockname, identifier, ex=lock_timeout, nx=True):
#             # print("线程:{}--拿到了锁".format(thread))
#             # if count <= 0:
#             #     print("没抢到票")
#             #     return False
#             # count -= 1
#             # print("线程:{}--抢到一张票，还剩{}张票".format(thread, count))
#             # cur = redis_client.get('rob-lock-1')
#
#             if int(redis_client.get('rob-lock-1').decode()) >= 1:
#                 redis_client.decr('rob-lock-1')
#                 # print("线程:{}--抢到一张票，还剩{}张票".format(thread, int(redis_client.get('rob-lock-1').decode()) - 1))
#                 return identifier  # 返回唯一标识
#             return False
#
#     return False
#
#
# def release_lock(conn, lockname, identifier):
#     """
#     释放锁
#
#     :param conn: Redis 连接
#     :param lockname: 锁的名称
#     :param identifier: 锁的标识
#     :return:
#     """
#     # python中redis事务是通过pipeline的封装实现的
#     with conn.pipeline() as pipe:
#         lockname = 'lock:' + lockname
#
#         while True:
#             try:
#                 # watch 锁,监听该锁, multi 后如果该 key 被其他客户端改变, 事务操作会抛出 WatchError 异常,使得当前客户端不会误删了别人的锁
#                 pipe.watch(lockname)
#                 ident = pipe.get(lockname)
#                 if ident and ident.decode('utf-8') == identifier:
#                     # 事务开始
#                     pipe.multi()
#                     pipe.delete(lockname)
#                     pipe.execute()
#                     return True
#
#                 pipe.unwatch()
#                 break
#             except WatchError:
#                 pass
#         return False
#
#
# redis_client = redis.Redis(host="127.0.0.1",
#                            port=6381,
#                            db=10)
# def seckill(i):
#
#     # print("线程:{}--想获取锁".format(i))
#     identifier=acquire_lock_with_timeout(redis_client, 'resource')
#     # if not identifier:
#     #     print(f"线程:{i}没抢到票")
#     # global count
#     # if count < 1:
#     #     print("线程:{}--没抢到，票抢完了".format(i))
#     #     return
#     # count -= 1
#     # print("线程:{}--抢到一张票，还剩{}张票".format(i, count))
#     release_lock(redis_client, 'resource', identifier)  # 释放这把锁
#
#
# for i in range(1000):
#     t = Thread(target=seckill,args=(i,))
#     t.start()
#
import contextlib
import time

print(int(time.time()))


def ttt(func):
    def decorate(self, sender, key):
        print(self)
        func(self, sender, key)

    return decorate


class Test():

    @ttt
    def test(self, sender, key):
        print(sender)
        print(key)


t = Test()
t.test(5, 6)


@contextlib.contextmanager
def manager_redis(db,  redis_class=None, redis=None,):
    try:
        # redis = get_redis_connection(db)  # redis实例链接

        yield db
    except Exception as e:
        return None
    finally:
        pass


def ttttt():
    with manager_redis(222) as db:
        ke = 'i am syz'
    return ke


l = ttttt()
print(l)


def save_search(test, sender, request, key, **kwargs):
    """
    记录某用户的浏览记录
    有效时间1个月
    """
    with manager_redis(test) as redis:
        # 为每个用户维护一个搜索有序集合
        pass


save_search(Test,222,222,333)