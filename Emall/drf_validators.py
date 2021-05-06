# -*- coding: utf-8 -*-
# @Time  : 2020/8/6 下午8:20
# @Author : 司云中
# @File : drf_validators.py
# @Software: Pycharm
import re

from rest_framework import serializers

from Emall.exceptions import DataNotExist


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


class ModelIdExist:
    """校验器：根据id搜索某数据是否存在"""
    def __init__(self, queryset, base):
        """
        初始化实例
        :param queryset: 初始查询集
        :param base: 数据所属model
        """
        self.queryset = queryset
        self.base = base

    def __call__(self, value):
        try:
            self.queryset.get(pk=value)
        except self.base.DoesNotExist:
            raise DataNotExist()


def validate_address_pk(value):
    """
    校验url中的关于address的pk字段
    一个用户只允许上限10个地址
    """
    return True if re.match('^[1-9]{0,10}$', str(value)) else False


def validate_commodity_pk(value):
    """
    校验url中的关于商品的pk字段
    商品id允许上限15位数
    """
    return True if re.match('^[1-9]\d{0,15}$', str(value)) else False


def validate_role_pid(value):
    """
    校验role中pid列表中的pid是否是字符串且个数为8位
    """
    try:
        if all(isinstance(item, str) and len(item) == 8 for item in set(value)):
            return True
    except Exception:
        return False

def validate_permission_pk(value):
    """
    校验url中的关于权限的pk字段
    权限id允许上限6位数
    """
    return True if re.match('^[1-9]\d{0,6}$', str(value)) else False

def validate_category_pk(value):
    """
    校验url中的关于商品类别的pk字段
    商品类别id允许上限5位数
    """
    return True if re.match('^[1-9]\d{0,5}$', str(value)) else False

def validate_commodity_group_pk(value):
    """
    检验url中的关于商品分组的pk字段
    商品类别id允许上限4位数
    """
    return True if re.match('^[1-9]\d{0,4}$', str(value)) else False

def validate_role_pk(value):
    """
    检验url中的关于商品分组的pk字段
    商品类别id允许上限4位数
    """

    return True if re.match('^[1-9]\d{0,4}$', str(value)) else False

def validate_sku_props_pk(value):
    """
    检验url中的关于商品属性的pk字段
    商品属性id允许上限8位数
    """
    return True if re.match('^[1-9]\d{0,7}$', str(value)) else False

def validate_freight_pk(value):
    """
    检验url中关于运费模板的pk字段
    运费模板id允许上线8位数
    """
    return True if re.match('^[1-9]\d{0,7}$', str(value)) else False


def validate_favorites_pk(value):
    """
    检验url中关于收藏夹的pk字段
    收藏夹id允许上限10位数
    """

    return True if re.match('^[1-9]\d{0,9}$', str(value)) else False

def validate_carousel_pk(value):
    """
    检验url中关于轮播图的pk字段
    轮播图允许上限4位数
    """

    return True if re.match('^[1-9]\d{0,3}', str(value)) else False


def validate_sku_pk(value):
    """
    检验url中关于SKU的pk字段
    轮播图允许上限9位数
    :param value:
    :return:
    """
    return True if re.match('^[1-9]\d{0,8}', str(value)) else False