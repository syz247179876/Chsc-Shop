from Emall.base_redis import manager_redis
from Emall.celery_app import app as celery_apps

__all__ = ['celery_apps','manager_redis']