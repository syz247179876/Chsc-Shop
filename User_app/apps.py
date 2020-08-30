from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'User_app'

    def ready(self):
        import User_app.redis.favorites_redis

