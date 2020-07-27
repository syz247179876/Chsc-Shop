import re



print(re.search(r'1[3456789]\d{9}$', '13511722028').group())

if re.match(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', '247179876@qq.com'):
    print('ues')

print(re.search(r'[a-zA-Z0-9]{6,20}', 'syz247179876'))


def kkk(m, k=None):
    print(k)


kkk(2,**{'k':'2'})



class Father:

    @classmethod
    def mm(cls):
        print(2,cls.__name__)


class Son(Father):

    @classmethod
    def mm(cls):
        super(Son, cls).mm()

Son.mm()

if re.match(r'^\?next=/(\w+)', '?next=/consumer/homepage'):
    print(re.match(r'^\?next=((/\w+)*)', '?next=/consumer/homepage').group(1))