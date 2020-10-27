# -*- coding: utf-8 -*- 
# @Time : 2020/6/2 12:19 
# @Author : 司云中 
# @File : shop.py 
# @Software: PyCharm
from shop_app.models.commodity_models import Commodity
from user_app.redis.foot_redis import FootRedisOperation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Emall.loggings import Logging
import markdown


login_required(login_url='consumer/login/')

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


def enter_introduction_page(request, pk):
    """进入到商品具体的详情页"""
    redis = FootRedisOperation.choice_redis_db('redis')
    if request.user.is_authenticated:
        user = request.user
        # 增加足迹
        is_success = redis.add_foot_commodity_id(user.pk, commodity_id=pk)
        if not is_success:
            consumer_logger.error('添加足迹失败')
    goods = Commodity.commodity_.select_related('store').get(pk=pk)

    goods.details = markdown.markdown(goods.details, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.attr_list',
        'markdown.extensions.smarty',
        'markdown.extensions.codehilite',  # 语法高亮拓展
        'markdown.extensions.toc',  # 自动生成目录
    ], safe_mode=True)  # 修改notes.note_contents内容为html
    price_now = goods.price * goods.discounts
    data = {
        'goods': goods,
        'price_now': price_now
    }
    return render(request, 'introduction.html', data)
