import re
import urllib

import requests

print(re.search(r'1[3456789]\d{9}$', '13511722028').group())

if re.match(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', '247179876@qq.com'):
    print('ues')

print(re.search(r'[a-zA-Z0-9]{6,20}', 'syz247179876'))


def kkk(m, k=None):
    print(k)


kkk(2, **{'k': '2'})


class Father:

    @classmethod
    def mm(cls):
        print(2, cls.__name__)


class Son(Father):

    @classmethod
    def mm(cls):
        super(Son, cls).mm()


Son.mm()

if re.match(r'^\?next=/(\w+)', '?next=/consumer/homepage'):
    print(re.match(r'^\?next=((/\w+)*)', '?next=/consumer/homepage').group(1))

m = re.search(r'^\w{0,5}', '啦啦啦了2')
n = re.match(r'\d', '3')
print(n)


class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        if nums is None:
            return []
        dict_ = {value: index for index, value in enumerate(nums)}
        for i in range(len(nums)):
            if (target - nums[i]) in dict_.keys() and i != dict_[target - nums[i]]:
                return [i, dict_.get(target - nums[i])]
        return []


s = Solution()
print(s.twoSum([2, 7, 11, 15], 9))

msss = r'^\w{5,20}$'
import re

print(re.fullmatch(msss, '斯文踩斯文踩斯文踩斯文踩斯文踩斯文踩'))


class A:

    def __init__(self):
        print(222222)

    @classmethod
    def test(cls):
        print('2222')


class B:
    def __init__(self):
        print(222)


def asss():
    try:
        ppp()
    except Exception as e:
        print(e)


asss()

import datetime

msss = datetime.datetime.now()
print(datetime.datetime.now())
print(
    '{third_year}{month}{day}{hour}{pk}{minute}{second}{microsecond}'.format(third_year=str(msss.year)[2:],
                                                                             month=str(msss.month),
                                                                             day=str(msss.day),
                                                                             hour=str(msss.hour),
                                                                             minute=str(msss.minute),
                                                                             second=str(msss.second),
                                                                             microsecond=str(msss.microsecond),
                                                                             pk=str(1)))
print(str(msss.month))
print(str(msss.day))
print(str(msss.hour))

try:
    msssss = 5
except:
    print(555)
print(msssss)

# response = requests.get('http://192.168.0.105:9200/shop/_search?q=text:商')
# m = response.json()
#
# hits = m.get('hits').get('hits')
# print([int(doc.get('_source').get('django_id')) for doc in hits])


# class ElasticSearchOperation(object):
#     """直接对es的请求封装"""
#
#     BASE_URL = 'http://192.168.0.105:9200/'
#     FUNC = '_search'
#     INDEX_DB = 'shop'
#
#     # __slots__ = ('query', '_instance', 'url')
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, '_instance'):
#             cls._instance = super().__new__(cls, *args, **kwargs)
#         return cls._instance
#
#     def __init__(self, **kwargs):
#         for key, value in kwargs:
#             pass
#
#     def tests(self):
#         # assert hasattr(self, 'query_params'), 'Should include query_params '
#         url = self.BASE_URL+self.INDEX_DB+'/'+self.FUNC + '?' + '&'.join([key+'='+value for key, value in {'syz':'bn','sda':'sadas'}.items()])
#         return url

# k = ElasticSearchOperation()
# k1 = ElasticSearchOperation()
# print(k1.tests())
#
# print(hash(k1) == hash(k))

aaa = lambda a, b, c: a + b + c
print(aaa(3, 4, 5))

dict_ = {3: 5}
print(str(dict_))


class ms:
    def __repr__(self):
        print(555)


kks = ms()
print(str(kks))
