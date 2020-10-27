# -*- coding: utf-8 -*-
# @Time  : 2020/8/20 下午3:26
# @Author : 司云中
# @File : json_serializer.py
# @Software: Pycharm


from datetime import datetime,date
import json
from decimal import Decimal
from uuid import UUID

class JsonCustomEncoder(json.JSONEncoder):
    """对时间序列等特殊序列进行编码序列化"""
    def default(self, obj):
        if type(obj) is None:
            return 'null'
        elif isinstance(obj,datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj,date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj,(Decimal,UUID,)):
            return str(obj)
        else:
            return super().default(obj)  # 抛出父类的异常

