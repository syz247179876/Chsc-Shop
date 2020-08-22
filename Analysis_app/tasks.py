# -*- coding: utf-8 -*-
# @Time  : 2020/8/22 下午8:03
# @Author : 司云中
# @File : tasks.py
# @Software: Pycharm

from e_mall.celery import app


@app.task
def task_statistic_login_times():
    """发送统计每日用户活跃量的定时信号"""

    pass
