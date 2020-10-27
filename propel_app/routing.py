# -*- coding: utf-8 -*-
# @Time  : 2020/8/8 下午4:22
# @Author : 司云中
# @File : routing.py
# @Software: Pycharm

from django.urls import path, re_path

websocket_urlpatterns = [
    # 官方解释path可能存在某种bug，用re_path既可以支持正则，也可以支持path路由匹配规则

    re_path(r'concern_notice',),   # 用户店铺关注，当店主上架新商品的时候进行商品推送
    re_path(r'buy_notice',),       # 当用户购买商品后，推送购买信息

]