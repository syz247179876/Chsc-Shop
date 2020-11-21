# -*- coding: utf-8 -*-
# @Time  : 2020/11/21 上午11:27
# @Author : 司云中
# @File : base_api.py
# @Software: Pycharm

"""
通用API共享函数
"""
from rest_framework import status
from rest_framework.response import Response

from Emall.response_code import response_code


def check_code(redis, validated_data):
    """校验验证码"""
    code_status = redis.check_code(validated_data.get('phone'), validated_data.get('code'))
    # 验证码错误或者过期
    if not code_status:
        return Response(response_code.verification_code_error, status=status.HTTP_400_BAD_REQUEST)