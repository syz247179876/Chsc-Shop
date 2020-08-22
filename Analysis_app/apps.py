from django.apps import AppConfig


class AnalysisAppConfig(AppConfig):
    name = 'Analysis_app'

    def ready(self):
        import Analysis_app.statistic
