# -*- coding: utf-8 -*- 
# @Time : 2020/5/26 20:40 
# @Author : 司云中 
# @File : order.py 
# @Software: PyCharm
import json

from Order_app.serializers.order_serializers import OrderAddressSerializer, OrderCommoditySerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from e_mall.loggings import Logging

# 控制台日志打印
common_logger = Logging.logger('django')

order_logger = Logging.logger('order_')


@login_required(login_url='/consumer/login/')
def personal_order(request):
    """进入用户空间的订单详情页"""
    return render(request, 'order.html')


def results(addresses):
    """地址结果"""
    return {
        'addresses': addresses
    }


@login_required(login_url='/consumer/login')
def personal_generate_order(request):
    """
    进入生成初始订单的页面，准备结算
    """
    user = request.user
    # goods_list = json.loads(request.body.decode('utf-8'))  # 解码 + 反序列化
    if request.session['commodity_list']:
        address_instances = OrderAddressSerializer.get_address(user)
        return render(request, 'pay.html', results(address_instances))
    else:
        return render(request, '404.html')
