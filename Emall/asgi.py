# -*- coding: utf-8 -*-
# @Time  : 2020/8/8 下午4:00
# @Author : 司云中
# @File : asgi.py.py
# @Software: Pycharm

import os
import django
from channels.routing import get_default_application


project_name = os.path.split(os.path.dirname(__file__))[-1]  # dirname当前目录的上一级==去掉文件名，返回目录
project_settings = "{}.settings".format(project_name)  # 获取setting配置文件

# 操作系统的环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Emall.settings")

django.setup()   # 加载异步application

application = get_default_application()
import django.conf.global_settings