# 暴露接口

from .celery import app as celery_app

__all__ = ['celery_app', 'tasks']
