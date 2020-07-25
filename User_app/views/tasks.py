# -*- coding: utf-8 -*-
# @Time : 2020/5/1 09:42
# @Author : 司云中
# @File : tasks.py
# @Software: PyCharm

import datetime
import string
from e_mall.settings import EMAIL_HOST_USER
from e_mall import celery_app as app
from django.core.mail import send_mail
import random


def set_verification_code() -> str:
    """Custom verification code"""
    code = ''
    # 设置随机种子
    random.seed(random.randint(1, 100))
    for i in range(6):
        m = random.randrange(1, 9)
        if i == m:
            code += str(m)
        else:
            code += random.choice(string.ascii_uppercase)
    return code


@app.task
def send_email_verification(title, content, user_email):
    """
    send email verification code
    title:标题
    content:内容
    user_email:对方邮箱
    """
    # fail_Silently为False表示会出错会报异常，方便捕捉
    send_mail(title, content, EMAIL_HOST_USER, [user_email], fail_silently=False)


@app.task
def send_phone_verification(title, content, phone):
    """send phone verification code"""
    pass


@app.task
def delete_outdated(self):
    """timed task:delete obsolete key-value"""
    now = datetime.datetime.now()
    delta = datetime.timedelta(-1)
    previous = now - delta
    key = previous.strftime('%Y-%m-%d')
    self.redis.delete(key)
