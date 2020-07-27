# -*- coding: utf-8 -*-
# @Time : 2020/5/2 12:25
# @Author : 司云中
# @File : validators.py
# @Software: PyCharm
import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class RecipientsValidator(validators.RegexValidator):
    """验证收件人"""
    regex = '^[\u4e00-\u9fa5]{0,10}$'
    message = _('验证人的名称不超过10个汉子')
    flags = 0

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


@deconstructible
class RegionValidator(validators.RegexValidator):
    """验证省份"""
    regex = '^[\u4e00-\u9fa5]{0,50}$'
    message = _('收货地址设置不超过50个汉子')
    flags = 0

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


class PhoneValidator(validators.RegexValidator):
    """验证手机号"""
    regex = '^13[0-9]{1}[0-9]{8}|^15[0-9]{1}[0-9]{8}'  # 正则表达式
    message = _('请输入正确的手机号格式')  # 错误提示消息
    flags = 0  # 修饰符

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


def username_validate(username):
    """用户名验证"""
    regex = r'[a-zA-Z0-9]{6,20}'
    if isinstance(username, str) and re.match(regex, username):
        return True
    return False


def password_validate(password):
    """密码验证"""
    regex = r'[a-zA-Z0-9]{8,20}'
    if isinstance(password, str) and re.match(regex, password):
        return True
    return False


def url_validate(url):
    """
    URL验证
    用于登录传递URL
    """
    regex = r'^\?next=((/\w+)*)'
    if isinstance(url, str) and re.match(regex, url):
        return url.split('?next=')[-1]
    return '/'   # 错误传回首页


def email_validate(email):
    """邮箱验证"""

    regex = r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*'
    if isinstance(email, str) and re.match(regex,email):
        return True
    return False


def phone_validate(phone):
    """手机号验证"""

    regex = r'^1[3456789]\d{9}$'
    if isinstance(phone, str) and re.match(regex, phone):
        return True
    return False



