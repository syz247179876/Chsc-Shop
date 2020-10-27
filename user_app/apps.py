from django.apps import AppConfig


class UserAppConfig(AppConfig):
    name = 'user_app'

    def ready(self):
        import user_app.redis.favorites_redis
