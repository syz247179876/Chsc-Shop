# -*- coding: utf-8 -*-
# @Time : 2020/7/22 10:38
# @Author : 司云中
# @File : single_mode.py
# @Software: PyCharm

# 单例模式的五大创建方法

# 第一种__new__魔法方法
class SingleMode1:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


# 第二种利用@classmethod装饰器
class SingleMode2:
    _instance = None

    @classmethod
    def create_obj(cls, *args, **kwargs):
        if not getattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


# 利用__dict__魔法方法将所有对象的__dict__设置成一样的
#
# class SingleMode3:
#     _default_dict = {}
#
#     def __new__(cls, *args, **kwargs):
#         obj = super().__new__(cls, *args, **kwargs)
#         obj.__dict__ = cls._default_dict
#         return obj

def single(cls):
    _instance = {}

    def generate_obj(*args, **kwargs):
        if _instance.setdefault(cls,None):
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return generate_obj


@single
class SingleMode4:
    pass


m1 = SingleMode1()

m2 = SingleMode1()

print(hash(m1) == hash(m2))

m3 = SingleMode2.create_obj()

m4 = SingleMode2.create_obj()

print(hash(m3) == hash(m4))

m5 = SingleMode4()

m6 = SingleMode4()

print(hash(m5) == hash(m6))


class m:
    def __init__(self):
        pass

print(len(dir(m)))



