# -*- coding: utf-8 -*-
# @Time  : 2020/11/14 下午7:51
# @Author : 司云中
# @File : signals.py
# @Software: Pycharm

from django.dispatch import Signal

# 记录搜索记录
record_search = Signal(providing_args=["request", "keyword"])

# 删除单个搜索记录
del_search_single = Signal(providing_args=["request", "key"])

# 删除所有搜索记录
del_search_all = Signal(providing_args=["request"])

# 获取记录数据
retrieve_record = Signal(providing_args=["request"])

# 获取热搜榜
retrieve_heat_keyword = Signal()

# 创建好商品，将指定信息添加到索引库中
add_to_es = Signal(providing_args=["id", "body"])

# 删除商品，将指定数据从索引库中删除
delete_from_es = Signal(providing_args=["id"])

# 更新商品，将指定数据同步更新到索引库中
update_to_es = Signal(providing_args=["id", "body"])

# 根据DSL，从索引库获取数据
retrieve_from_es = Signal(providing_args=["body"])