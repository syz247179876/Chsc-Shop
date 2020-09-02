# import collections
# import re
#
# print(re.search(r'1[3456789]\d{9}$', '13511722028').group())
#
# if re.match(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', '247179876@qq.com'):
#     print('ues')
#
# print(re.search(r'[a-zA-Z0-9]{6,20}', 'syz247179876'))
#
#
# def kkk(m, k=None):
#     print(k)
#
#
# kkk(2, **{'k': '2'})
#
#
# class Father:
#
#     @classmethod
#     def mm(cls):
#         print(2, cls.__name__)
#
#
# class Son(Father):
#
#     @classmethod
#     def mm(cls):
#         super(Son, cls).mm()
#
#
# Son.mm()
#
# if re.match(r'^\?next=/(\w+)', '?next=/consumer/homepage'):
#     print(re.match(r'^\?next=((/\w+)*)', '?next=/consumer/homepage').group(1))
#
# m = re.search(r'^\w{0,5}', '啦啦啦了2')
# n = re.match(r'\d', '3')
# print(n)
#
#
# class Solution(object):
#     def twoSum(self, nums, target):
#         """
#         :type nums: List[int]
#         :type target: int
#         :rtype: List[int]
#         """
#         if nums is None:
#             return []
#         dict_ = {value: index for index, value in enumerate(nums)}
#         for i in range(len(nums)):
#             if (target - nums[i]) in dict_.keys() and i != dict_[target - nums[i]]:
#                 return [i, dict_.get(target - nums[i])]
#         return []
#
#
# s = Solution()
# print(s.twoSum([2, 7, 11, 15], 9))
#
# msss = r'^\w{5,20}$'
# import re
#
# print(re.fullmatch(msss, '斯文踩斯文踩斯文踩斯文踩斯文踩斯文踩'))
#
#
# class A:
#
#     def __init__(self):
#         print(222222)
#
#     @classmethod
#     def test(cls):
#         print('2222')
#
#
# class B:
#     def __init__(self):
#         print(222)
#
#
# def asss():
#     try:
#         ppp()
#     except Exception as e:
#         print(e)
#
#
# asss()
#
# import datetime
#
# msss = datetime.datetime.now()
# print(datetime.datetime.now())
# print(
#     '{third_year}{month}{day}{hour}{pk}{minute}{second}{microsecond}'.format(third_year=str(msss.year)[2:],
#                                                                              month=str(msss.month),
#                                                                              day=str(msss.day),
#                                                                              hour=str(msss.hour),
#                                                                              minute=str(msss.minute),
#                                                                              second=str(msss.second),
#                                                                              microsecond=str(msss.microsecond),
#                                                                              pk=str(1)))
# print(str(msss.month))
# print(str(msss.day))
# print(str(msss.hour))
#
# try:
#     msssss = 5
# except:
#     print(555)
# print(msssss)
#
# # response = requests.get('http://192.168.0.105:9200/shop/_search?q=text:商')
# # m = response.json()
# #
# # hits = m.get('hits').get('hits')
# # print([int(doc.get('_source').get('django_id')) for doc in hits])
#
#
# # class ElasticSearchOperation(object):
# #     """直接对es的请求封装"""
# #
# #     BASE_URL = 'http://192.168.0.105:9200/'
# #     FUNC = '_search'
# #     INDEX_DB = 'shop'
# #
# #     # __slots__ = ('query', '_instance', 'url')
# #     def __new__(cls, *args, **kwargs):
# #         if not hasattr(cls, '_instance'):
# #             cls._instance = super().__new__(cls, *args, **kwargs)
# #         return cls._instance
# #
# #     def __init__(self, **kwargs):
# #         for key, value in kwargs:
# #             pass
# #
# #     def tests(self):
# #         # assert hasattr(self, 'query_params'), 'Should include query_params '
# #         url = self.BASE_URL+self.INDEX_DB+'/'+self.FUNC + '?' + '&'.join([key+'='+value for key, value in {'syz':'bn','sda':'sadas'}.items()])
# #         return url
#
# # k = ElasticSearchOperation()
# # k1 = ElasticSearchOperation()
# # print(k1.tests())
# #
# # print(hash(k1) == hash(k))
#
# aaa = lambda a, b, c: a + b + c
# print(aaa(3, 4, 5))
#
# dict_ = {3: 5}
# print(str(dict_))
#
#
# class ms:
#     id = '2'
#
#     def tests(self):
#         return 'API...' + self.id
#
#     def custom_button(self):
#         pass
#
#     custom_button.action_url = tests
#
#
# kks = ms()
# kks.custom_button()
# print(kks.custom_button.action_url(kks))
#
#
# class ts(collections.abc.Sequence):
#     tests = [1, 2, 3, 5, 6]
#
#     def __len__(self):
#         return len(self.tests)
#
#     def __getitem__(self, item):
#         return self.tests[item]
#
#     @classmethod
#     def test(cls):
#         print(555)
#
#
# tss = ts()
# tss.test()
#
# from collections import defaultdict
#
#
# class classmethodss(classmethod):
#
#     def __new__(cls, *args, **kwargs):
#         pass
#
#
# class test:
#     kk = 2131222
#
#     @classmethod
#     def m(cls):
#         cls.name = '55522'
#
#     def __init__(self):
#         self.kk = 2131
#
#
# from fdfs_client.client import *
#
# client = Fdfs_client('/etc/fdfs/client.conf')
# print(client)
#
#
# def example(request):
#     # TODO 数据库操作
#
#     pass
import time
from decimal import Decimal

# print(time.mktime(time.strptime('2020-05-20 13:25:35', "%Y-%m-%d %H:%M:%S")))
#
# import json
#
#
# class Person(object):
#
#     def __init__(self, name, gender):
#         self.name = name
#         self.gender = gender
#
#
# p = Person("Tom", "female")
#
# str_p = json.dumps(p, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)
# print(str_p)
#
# import datetime
# import time
# print(time.mktime(datetime.datetime.now().timetuple()))
#
# k = {'2':'2', '3':'3', '4':'4'}
# for i in iter(k):
#     print(i)
#
# kss = '2' in k
# print(kss)
#
#
# m = {'user': 3,
#  'head_image': 'group1/M00/00/00/wKgAaV86kJ-ARxCAAA543lGjCZc7153661',
#  'birthday': datetime.date(1999, 5, 20),
#  'sex': 'm',
#  'phone': '13787833290',
#  'rank': '1',
#  'safety': Decimal('60'),
#  'nationality': '汉'}
#
# from e_mall import json_serializer
#
# k = json.dumps(m, cls=json_serializer.JsonCustomEncoder)
# print(k)
#
#
# print(any({'r':None}))
# print()
#
# def kkk(syz=None):
#     print(syz)
#
# kkk(**{'syz':2222})
#
# kkkks=  [{b'store': b'1', b'shopper': b'2', b'commodity_name': b'\xe7\x89\x9b\xe8\x82\x89\xe5\xb9\xb2', b'price': b'15', b'details': b'111', b'intro': b'111', b'category': b'\xe9\xa3\x9f\xe5\x93\x81', b'status': b'1', b'onshelve_time': b'2020-08-10 20:06:35', b'unshelve_time': b'2020-08-10 20:06:35', b'discounts': b'1.0', b'sell_counts': b'0', b'freight': b'3', b'image': b'commodity_head/niu_u8LcWku.jpg', b'discounts_intro': b'\xe8\xaf\xa5\xe5\xba\x97\xe9\x93\xba\xe7\x9b\xae\xe5\x89\x8d\xe6\x9a\x82\xe6\x97\xa0\xe4\xbc\x98\xe6\x83\xa0\xe6\xb4\xbb\xe5\x8a\xa8', b'stock': b'5000', b'pk': b'26543'}, {b'store': b'1', b'shopper': b'2', b'commodity_name': b'\xe7\x89\x9b\xe8\x82\x89\xe5\xb9\xb2', b'price': b'15', b'details': b'111', b'intro': b'111', b'category': b'\xe9\xa3\x9f\xe5\x93\x81', b'status': b'1', b'onshelve_time': b'2020-08-10 20:06:35', b'unshelve_time': b'2020-08-10 20:06:35', b'discounts': b'1.0', b'sell_counts': b'0', b'freight': b'3', b'image': b'commodity_head/niu_u8LcWku.jpg', b'discounts_intro': b'\xe8\xaf\xa5\xe5\xba\x97\xe9\x93\xba\xe7\x9b\xae\xe5\x89\x8d\xe6\x9a\x82\xe6\x97\xa0\xe4\xbc\x98\xe6\x83\xa0\xe6\xb4\xbb\xe5\x8a\xa8', b'stock': b'5000', b'pk': b'26543'}]
#
# def format_data(data):
#     """格式化数据"""
#     if isinstance(data, list):
#         data = [{key.decode():value.decode() for key, value in orderdict.items() if not isinstance(value,str)} for orderdict in data]
#     return json.dumps(data)
# print(format_data(kkkks))
#
# print(datetime.date.strftime(datetime.date.today()-datetime.timedelta(1),"%Y-%m-%d"))
#
# print(type(eval('[23]')))
#
#
# class JSONString(object):
#     def __new__(self, value):
#         ret = str.__new__(self, value)
#         ret.is_json_string = True
#         return ret
#     def __getattribute__(self, item):
#
#
# KKSS = JSONString('3333')
# print(KKSS.is_json_string)
#
#
# kkkks = {
#     'name':'syz'
# }
#
#
# def test(kkks):
#     print(2222)
#     kkks.update({'2222':2})
#
#     return kkks
#
# test.kkk = kkkks
#
# mms = test(kkkks)
# mmss = test(kkkks)
# mmkk = test({2:2})
# print(id(mms) == id(mmss))
# print(mms,mmss,mmkk)

class Test(object):
    sss = 's'
    def __getattribute__(self, item):
        # v = object.__getattribute__(self, item)
        # # if hasattr(v, '__get__'):
        # #     return v.__get__(None, self)
        # return v
        raise AttributeError('syz')
        # return 'syz'
    def __getattr__(self, item):
        return item
    def __get__(self, instance, owner):
        print(instance,owner)
        return 'love'

class Operation(object):

    t = Test()

m = Operation()
# print(m.t,'|',type(m.t))
print(m.t)
print(m.__dict__)

test = Test()
print(test.__dict__)
# print(test.sss)
# print(getattr(test,'sss') == test.sss)

# class Emm:
#     def __init__(self):
#         self._name = 'syz'
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, value):
#         self._name = value
#
#     @name.deleter
#     def name(self):
#         del self._name


# emm = Emm()
# print(emm.__dict__)
# print(emm.name)
# emm.name = 'zjw'
# print(emm.name)
# del emm.name
# print(emm.__dict__)

class Property(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)




# class Emm:
#     def __init__(self):
#         self._name = 'syz'
#
#     @Property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, value):
#         self._name = value
#
#     @name.deleter
#     def name(self):
#         del self._name
#
#
# emm = Emm()
# print(emm.__dict__)
# print(emm.name)
# emm.name = 'zjw'
# print(emm.name)
# del emm.name
# print(emm.__dict__)
print(False == False)