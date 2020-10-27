from django.apps import AppConfig


class VoucherAppConfig(AppConfig):
    name = 'voucher_app'

    def ready(self):
        from voucher_app import utils
