# -*- coding: utf-8 -*-
# @Time  : 2020/8/6 下午8:20
# @Author : 司云中
# @File : drf_validators.py
# @Software: Pycharm
import re

from rest_framework import serializers


class DRFBaseValidator:
    """基验证器"""
    regex = None  # 正则表达式
    message = None  # 错误消息提示
    type = str  # 值所属的类型
    re_method = 'match'  # 默认的re方法

    def __call__(self, value):
        assert self.message is not None, (
            'Regex , Message and Type cannot be empty,'
            'Regex means regular string,'
            'Message means error notice,'
            'Type means the type to which the value belong'
        )
        if not isinstance(value, self.type) or not getattr(re, self.re_method)(self.regex, value):
            raise serializers.ValidationError(self.message)