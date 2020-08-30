from django.apps import AppConfig


class RemarkConfig(AppConfig):
    name = 'Remark_app'

    def ready(self):
        import Remark_app.redis.remark_redis
