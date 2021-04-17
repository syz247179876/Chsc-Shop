# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午5:54
# @Author : 司云中
# @File : common.py
# @Software: Pycharm

def identity(func):
    """
    根据用户登录修改identity
    如果用户尚未登录
    返回空数据,由后续装饰器来获取ip地址作为唯一身份标识
    """

    def decorate(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            identity = request.user.pk
        else:
            identity = None
        return func(self, request, identity, *args, **kwargs)
    return decorate