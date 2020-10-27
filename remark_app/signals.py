# -*- coding: utf-8 -*-
# @Time  : 2020/8/30 下午5:50
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm

from django.dispatch import Signal

praise_or_against_post = Signal(providing_args=["pk", "user"])

praise_or_against_cancel = Signal(providing_args=["pk", "user"])

remark_post = Signal(providing_args=["commodity_pk", "user"])

remark_cancel = Signal(providing_args=["commodity_pk", "user"])

check_remark_action = Signal(providing_args=["pk", "user", "is_remark", "is_action"])  # 包含评论 or  点赞/反对