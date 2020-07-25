import base64
import datetime
import logging
import random
from abc import ABC
from functools import reduce
from urllib import parse

from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import make_password

m = '%E5%9B%BE%E6%A0%87'

k = parse.unquote(m, encoding='utf-8')
print(k)


class test:

    def t(self):
        self.m = 5


class test2(test):

    def f(self):
        self.m = 6


ts = test2()

ts.f()
print(ts.m)

m = datetime.datetime.now().year
print(type(m))


def max_year():
    cur_year = datetime.datetime.now().year
    delta = relativedelta(year=16).year
    return cur_year - delta


def kkkk(list_):
    list_.append(22)


k = [2, 3, 4, 5]
kkkk(k)
print(k)

m = '?next=/consumer/personal_information/'
k = m.split('?next=')
print(k[-1])

dict_ = {
    'name': 'syz'
}
print(dict_.get('name'))

import datetime

m = datetime.datetime.strptime('2019-05-20', '%Y-%m-%d')
print(type(m))

m = random.randint(1, 9)
print(m)

kws = {'name': 'syz', 'ages': 19}


def m(name, age, *args, **kwargs):
    print(name, args, kwargs)


m('sss', 19, agsss=20, kkk=3333)


class send_code:
    """decorator for sending code"""

    def __init__(self, mode):
        """mode choose from any function"""
        self.mode = mode

    def __call__(self, func):
        def send(obj, way, key, **kwargs):
            """way choose from email and phone"""
            status = func(obj, key, **kwargs)
            print(status)

        return send


class testtt:
    m = None

    @send_code('register')
    def mm(self, key, **kwargs):
        return 6666


class testttt(testtt):
    m = 'ssss'


test = testttt()
print(test.m)


class Singleton(object):
    ''''' A python style singleton '''

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            org = super()
            print(type(org))
            print(org.__doc__)
            print(cls.__doc__)
            cls._instance = org.__new__(cls, *args, **kw)
        return cls._instance


s = Singleton()


def urlencode(hosturl, name):
    params = []
    for k, v in name.items():
        params.append(k + '=' + v)
    return hosturl + '?' + '&'.join(params)


k = urlencode('www.baidu.com/', {'name': 'syz', 'age': "20"})

print(k)

k = lambda hosturl, name: hosturl + '?' + '&'.join((k + '=' + v for k, v in name.items()))

print(k('www.baidu.com/', {'name': 'syz', 'age': "20"}))


class Logging:
    _instance = {}

    @classmethod
    def get_logger(cls, logger_name):
        return cls._instance[logger_name]

    @classmethod
    def logger(cls, logger_name):
        if not cls._instance.setdefault(logger_name, None):
            cls._instance[logger_name] = logging.getLogger(logger_name)
        return cls._instance[logger_name]


test = Logging.logger('django')
print(test)

m = Logging.logger('django')
print(id(m) == id(test))

k = {'syz': 22, 'age': 222}


def fff(**kwargs):
    print(kwargs)


fff(k=5, ww=22, **k)

func_dict = {
    'default': 'put_default_address',
    'edit': 'put_edit_address'
}

print(func_dict.get('default'))

"""m = b'{"address":"\xe6\xb1\x9f\xe8\x8b\x8f\xe7\x9c\x81\xe4\xbb\xaa\xe5\xbe\x81\xe5\xb8\x82\xe7\x99\xbd\xe6\xb2\x99\xe8\xb7\xaf\xe6\xb5\xa6\xe4\xb8\x9c\xe4\xb8\x89\xe6\x9d\x9120\xe5\xb9\xa2501\xe5\xae\xa4","birth":"19990520","card_region":[{"x":209,"y":473},{"x":2577,"y":438},{"x":2597,"y":1838},{"x":230,"y":1873}],"config_str":"{\\"side\\":\\"face\\"}","face_rect":{"angle":-0.29902634024620056,"center":{"x":2092.114990234375,"y":1046.6751708984375},"size":{"height":421.97091674804688,"width":381.798828125}},"face_rect_vertices":[{"x":1900,"y":836},{"x":2281,"y":834},{"x":2284,"y":1256},{"x":1902,"y":1258}],"name":"\xe5\x8f\xb8\xe4\xba\x91\xe4\xb8\xad","nationality":"\xe6\xb1\x89","num":"321081199905208418","request_id":"20200509154117_bb034cf2514d74c2525e925f043cd543","sex":"\xe7\x94\xb7","success":true}'

k = m.decode('utf-8')
print(json.loads(k))"""

image = bytes('我', encoding='utf-8')
print(image)

import pickle

m = pickle.dumps('face')
kkk = str(base64.b64encode(m), encoding='utf-8')
print(m)

print(kkk)


class test:
    mm = 'syz'

    @staticmethod
    def test_func(name, age):
        print(name, age)


m = test()

m.test_func('syz', 20)
test.test_func('syz', 20)

m.mm = 'zjw'
print(m.mm)
print(test.mm)


def test(**kwargs):
    print(kwargs)


test(name='name', age=10)

n = {'name': 'image'}

print(n.setdefault('2', 2))
print(n)


def te():
    try:
        if 6 > 5:
            print(22)
    except Exception as e:
        print(e)
    else:
        return 5
    finally:
        print(5333)


m = te()
print(m)
import time

m = time.time()


def mm(limit, page):
    today = datetime.datetime.now()  # 以今天date为基础
    max_timedelta = datetime.timedelta(limit * (page - 1))
    min_timedelta = datetime.timedelta(limit * page)
    min_score = today - min_timedelta
    max_score = today - max_timedelta
    print(min_score)
    m = min_score.strftime("%Y-%m-%d")
    print(time.mktime(time.strptime(m, "%Y-%m-%d")))


mm(2, 1)

print(datetime.datetime.fromtimestamp(1590508800))


def kkkk(*args):
    keywords = (str(value) if not isinstance(value, str) else value for value in args)

    key = '-'.join(keywords)
    return key
kkkkk = {'name':'syz'}
www=kkkkk.update({'age':2})
print(kkkkk)


print(int(2312))