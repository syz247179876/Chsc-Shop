# -*- coding: utf-8 -*-
# @Time  : 2020/8/14 上午9:29
# @Author : 司云中
# @File : tasks.py
# @Software: Pycharm

import random
import string
import uuid

from django.core.mail import send_mail

from e_mall import celery_apps as app
from e_mall.send_sms import send_sms
from e_mall.settings import EMAIL_HOST_USER
from e_mall.settings import SIGN_NAME


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
def send_phone(phone_numbers, template_code, template_param):
    _business_id = uuid.uuid1()
    send_sms(_business_id, phone_numbers=phone_numbers, sign_name=SIGN_NAME, template_code=template_code,
             template_param=template_param)


@app.task
def send_email(title, content, user_email):
    """
    send email verification code
    title:标题
    content:内容
    user_email:对方邮箱
    """
    # fail_Silently为False表示会出错会报异常，方便捕捉
    send_mail(title, content, EMAIL_HOST_USER, [user_email], fail_silently=False)
