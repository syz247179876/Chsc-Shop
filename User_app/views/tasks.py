# -*- coding: utf-8 -*-
# @Time : 2020/5/1 09:42
# @Author : 司云中
# @File : tasks.py
# @Software: PyCharm

import datetime
import time

from User_app.views.ali_card_ocr import Interface_identify
from e_mall import celery_app as app


# @app.task
# def delete_outdated(self):
#     """timed task:delete obsolete key-value"""
#     now = datetime.datetime.now()
#     delta = datetime.timedelta(-1)
#     previous = now - delta
#     key = previous.strftime('%Y-%m-%d')
#     self.redis.delete(key)

@app.task
def ocr(image_instance, type_):
    """
    身份验证
    :param image_instance: InMemoryUploadedFile 文件对象
    :param type_: String 身份证类型 face or back
    :return:  Bool
    """
    identify_instance = Interface_identify(image_instance, type_)
    return identify_instance.is_success

