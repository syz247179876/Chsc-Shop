from django.apps import AppConfig


class SearchAppConfig(AppConfig):
    name = 'search_app'

    def ready(self):
        import search_app.redis.history_redis
        print(23213312)
