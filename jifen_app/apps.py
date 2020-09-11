from django.apps import AppConfig


class JifenAppConfig(AppConfig):
    name = 'jifen_app'

    def ready(self):
        from jifen_app import utils
