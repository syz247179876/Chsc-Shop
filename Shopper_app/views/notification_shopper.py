"""
自定义信号函数
"""
from django.dispatch import receiver
from django.db.models import signals
from notifications.signals import notify
from notifications import models as notification

from django.core.signals import request_finished


@receiver(request_finished)
def my_callback(sender, **kwargs):
    print("Request finished")
