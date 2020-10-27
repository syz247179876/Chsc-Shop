# -*- coding: utf-8 -*-
# @Time  : 2020/8/19 上午9:23
# @Author : 司云中
# @File : utils.py
# @Software: Pycharm
import json


class FootRedisEncoder(json.JSONEncoder):
    """对足迹redis类进行序列化"""

    def default(self, obj):
        return {

        }
