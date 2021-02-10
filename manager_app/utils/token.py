# -*- coding: utf-8 -*-
# @Time  : 2021/2/9 下午11:52
# @Author : 司云中
# @File : token.py
# @Software: Pycharm

def generate_payload(user):
    """为不同权限的管理者生成不同的token"""
    username = "role"
    payload = {
        username:''
    }