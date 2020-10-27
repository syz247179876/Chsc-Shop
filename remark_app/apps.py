from django.apps import AppConfig


class RemarkAppConfig(AppConfig):
    name = 'remark_app'

    def ready(self):
        import remark_app.redis.remark_redis