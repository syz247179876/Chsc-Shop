from django.apps import AppConfig

from e_mall.loggings import Logging

class UserConfig(AppConfig):
    name = 'User_app'

    def ready(self):
        import User_app.redis.favorites_redis

