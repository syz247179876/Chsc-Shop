# -*- coding: utf-8 -*-
# @Time : 2020/5/2 12:25
# @Author : 司云中
# @File : validators.py
# @Software: PyCharm
import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

# Django 验证器, 用于表单验证-ModelForm,Model中无反应
from rest_framework import serializers

# deconstructible对该类进行序列化，确保migration的正确性
from e_mall.drf_validators import DRFBaseValidator


@deconstructible
class RecipientsValidator(validators.RegexValidator):
    """
    验证收件人
    """
    regex = r'^[\u4e00-\u9fa5]{1,10}$'
    message = _('验证人的名称必须在1～10个汉字之间')
    flags = 0

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


@deconstructible
class RegionValidator(validators.RegexValidator):
    """验证收货地址"""
    regex = r'^\w{0,50}$'
    message = _('收货地址设置不超过50个汉子')
    flags = 0

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


@deconstructible
class PhoneValidator(validators.RegexValidator):
    """验证手机号"""
    regex = r'^13[0-9]{1}[0-9]{8}|^15[0-9]{1}[0-9]{8}'  # 正则表达式
    message = _('请输入正确的手机号格式')  # 错误提示消息
    flags = 0  # 修饰符

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


@deconstructible
class AddressTagValidator(validators.RegexValidator):
    """验证地址标签"""
    regex = r'[123]'
    message = _('请选择正确的地址标签编号')
    flags = 0

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)


# DRF 验证器


class DRFUsernameValidator(DRFBaseValidator):
    """用户名验证"""
    regex = r'^[\w.@+-]+$'  # 限制结尾必须是正确的数，否则用fullmatch
    message = _('用户名格式不正确,只能包含字符，数字，以及@/./+/-/_ ')


class DRFPasswordValidator(DRFBaseValidator):
    """密码验证"""
    regex = r'^[a-zA-Z0-9]{8,20}$'
    message = _('密码格式不正确')
    re_method = 'fullmatch'


class DRFPhoneValidator(DRFBaseValidator):
    """手机号验证"""
    regex = '^13[0-9]{1}[0-9]{8}|^15[0-9]{1}[0-9]{8}$'
    message = _('手机号格式不正确')
    re_method = 'fullmatch'


class DRFEmailValidator(DRFBaseValidator):
    """邮箱验证"""
    regex = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
    message = _('邮箱格式不正确')


class DRFPkValidator(DRFBaseValidator):
    """对象PK验证"""
    regex = r'\d{1,10}'
    message = _('pk应为正整数')


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
    return '/'  # 错误传回首页


def email_validate(email):
    """邮箱验证"""

    regex = r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*'
    if isinstance(email, str) and re.match(regex, email):
        return True
    return False


def phone_validate(phone):
    """手机号验证"""

    regex = r'^1[3456789]\d{9}$'
    if isinstance(phone, str) and re.match(regex, phone):
        return True
    return False
