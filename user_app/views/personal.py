# -*- coding: utf-8 -*-
# @Time : 2020/5/5 13:21
# @Author : 司云中
# @File : personal.py
# @Software: PyCharm

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from user_app.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from user_app.models import Address
from Emall.loggings import Logging
import datetime
from dateutil.relativedelta import relativedelta

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')
@cache_page

def range_year():
    """允许注册用户的合法年龄"""
    cur_year = datetime.datetime.now().year
    max_delta = relativedelta(year=16).year
    min_delta = relativedelta(year=70).year

    max_year = cur_year - max_delta
    min_delta = cur_year - min_delta
    return max_year, min_delta


@login_required(login_url='/consumer/login/')
def personal(request):
    """进入个人空间主页"""
    return render(request, 'personal.html')


@login_required(login_url='/consumer/login/')
def personal_address(request):
    """进入个人地址页"""
    addresses = Address.address_.filter(user=request.user)
    data = {
        'addresses': addresses
    }
    return render(request, 'address.html', data)


@login_required(login_url='/consumer/login/')
def edit_address(request, pk):
    try:
        address = Address.address_.get(pk=int(pk), user=request.user)
    except Exception:
        return HttpResponseForbidden()  # 接口调用他人地址没有权限
    else:
        region = address.region.split('-')
        area = region[0]
        province = region[1]
        city = region[2]
        dist = region[3]
        intro = region[4]
        data = {
            'address': address,
            'area': area,
            'province': province,
            'city': city,
            'dist': dist,
            'intro': intro
        }
        return render(request, 'edit-address.html', data)


@login_required(login_url='/consumer/login/')
def personal_information(request):
    """进入个人详细信息页"""
    try:
        user = User.objects.get(pk=request.user.pk)
        username = user.get_username()
        actual_name = user.get_short_name()
        email = user.get_email()
        rank = user.consumer.get_rank_display()
        sex = user.consumer.get_sex_display()
        head_image = user.consumer.get_head_image
        phone = user.consumer.get_phone
        safety = user.consumer.safety
        birthday = user.consumer.birthday
        if birthday:
            birthday = birthday.strftime('%Y-%m-%d')
        else:
            birthday = ''
    except User.DoesNotExist:
        return HttpResponseForbidden()
    data = {
        'username': username,
        'actual_name': actual_name,
        'email': email,
        'sex': sex,
        'head_image': head_image,
        'phone': phone,
        'rank': rank,
        'safety': safety,
        'birthday': birthday,
    }

    return render(request, 'information.html', context=data)


@login_required(login_url='/consumer/login/')
def personal_safety(request):
    """进入个人安全页"""
    try:
        user = User.objects.get(pk=request.user.pk)
        username = user.get_username()
        rank = user.consumer.get_rank_display()
        safety = user.consumer.safety
    except User.DoesNotExist:
        return HttpResponseForbidden()

    data = {
        'username': username,
        'rank': rank,
        'safety': safety,
    }

    return render(request, 'safety.html', context=data)


@login_required(login_url='/consumer/login/')
def personal_password(request):
    """进入个人密码页"""
    return render(request, 'password.html')


@login_required(login_url='/consumer/login/')
def personal_setpay(request):
    """进入个人支付密码页（可以删除）"""
    user = User.objects.get(pk=request.user.pk)
    phone_pre = user.consumer.get_phone[0:3]
    phone_suffix = user.consumer.get_phone[-4:]
    data = {
        'phone_pre': phone_pre,
        'phone_suffix': phone_suffix,
    }
    return render(request, 'setpay.html', data)


@login_required(login_url='/consumer/login/')
def personal_bindphone(request):
    """进入手机绑定页"""
    user = User.objects.get(pk=request.user.pk)
    phone = user.consumer.get_phone
    phone_pre = phone[0:3]
    phone_suffix = phone[-4:]
    data = {
        'phone': phone,
        'phone_pre': phone_pre,
        'phone_suffix': phone_suffix,
    }

    return render(request, 'bindphone.html', data)


@login_required(login_url='/consumer/login/')
def personal_bindemail(request):
    """进入邮箱绑定页"""
    email = request.user.get_email()
    data = {
        'email': email
    }
    return render(request, 'bindemail.html', data)


@login_required(login_url='/consumer/login/')
def personal_idcard(request):
    """进入密码修改页"""
    username = request.user.get_username()
    actual_name = request.user.first_name
    data = {
        'username': username,
        'is_verify': 0,
        'actual_name': actual_name,
    }
    if actual_name:
        data.update({'actual_name': actual_name, 'is_verify': 1})
    return render(request, 'idcard.html', data)


@login_required(login_url='/consumer/login/')
def personal_question(request):
    """进入个人密保页（可以删除）"""

    return render(request, 'question.html')


@login_required(login_url='/consumer/login/')
def personal_bill(request):
    """进入个人消费资金页"""
    return render(request, 'bill.html')


@login_required(login_url='/consumer/login/')
def personal_bonus(request):
    """进入个人购物卷页"""
    return render(request, 'bonus.html')


@login_required(login_url='/consumer/login/')
def personal_change(request):
    """进入个人退货管理页"""
    return render(request, 'change.html')


@login_required(login_url='/consumer/login/')
def personal_collection(request):
    """进入个人收藏夹页"""
    return render(request, 'collection.html')


@login_required(login_url='/consumer/login/')
def personal_foot(request):
    """进入个人足迹页"""
    return render(request, 'foot.html')


@login_required(login_url='/consumer/login/')
def personal_coupon(request):
    """进入个人优惠卷页"""
    return render(request, 'coupon.html')


@login_required(login_url='/consumer/login/')
def personal_shopcart(request):
    """进入个人购物车页"""
    return render(request, 'shopcart.html')


@login_required(login_url='/consumer/login/')
def logout_mall(request):
    """退出商城，重定向到首页"""
    logout(request)  # 清除request.user和对应的request.session
    return redirect('/')

