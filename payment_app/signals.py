# -*- coding: utf-8 -*-
# @Time  : 2020/9/11 上午9:57
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm


from django.dispatch import Signal

save_payment = Signal(providing_args=["instance", "trade_id"])