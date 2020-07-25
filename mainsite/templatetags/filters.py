# -*- coding: utf-8 -*- 
# @Time : 2020/6/1 15:46 
# @Author : 司云中 
# @File : filters.py 
# @Software: PyCharm

from django import template
from e_mall.loggings import Logging

register = template.Library()

common_logger = Logging.logger('django')


@register.filter(name='cut_address')
def cut_address(value, arg):
    """根据arg索引下标切割地址中的具体省份，城市"""
    # return ' '.join([value[int(i)] for i in arg])
    value_list = value.split('-')
    return '{} {}'.format(value_list[arg],value_list[arg+1])
