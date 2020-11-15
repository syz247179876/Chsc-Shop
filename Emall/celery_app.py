# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : celery.py
# @Software: PyCharm

# 绝对导入，把下一个新版本的特性导入到当前版本，例如python3取消了python2.u前缀
from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from os import path, environ

from Emall.settings import BROKER_URL

project_name = path.split(path.dirname(__file__))[-1]  # dirname当前目录的上一级==去掉文件名，返回目录
project_settings = "{}.settings".format(project_name)  # 获取setting配置文件

# 设置环境变量，让django能够识别启动celery.py这个文件
environ.setdefault("DJANGO_SETTINGS_MODULE", project_settings)

# 实例化Celery
app = Celery('tasks', broker=BROKER_URL)

# 使用django的settings文件配置celery，一些基础参数，比如任务队列存放的位置redis中，执行返回的结果保存的位置，BROKER_URL，CELERY_RESULT_BACKEND等
app.config_from_object("django.conf.settings", namespace='CELERY')

# Celery利用反射机制扫描加载所有注册的应用
app.autodiscover_tasks(settings.INSTALLED_APPS_PACKAGES)
