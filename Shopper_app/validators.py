import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


# 该类装饰器用于在自定义存储系统时候迁移进行序列化
from django.core.exceptions import ValidationError


class PhoneValidator(validators.RegexValidator):
    """正则表达式验证"""
    regex = '^13[0-9]{1}[0-9]{8}|^15[0-9]{1}[0-9]{8}'  # 正则表达式
    message = _('请输入正确的手机号格式') # 错误提示消息
    flags = 0  # 修饰符

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex,message,flags)

def validate_sex(value):
    """验证性别"""
    if value != 'm' and value != 'f':
        raise ValidationError(
            _('该字段值 必须是性别'),
        )
