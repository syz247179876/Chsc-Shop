from django.apps import AppConfig


class VoucherAppConfig(AppConfig):
    name = 'Voucher_app'

    def ready(self):
        from Voucher_app import utils
