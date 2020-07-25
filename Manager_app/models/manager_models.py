from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from django.utils import timezone


'''
class Manager_user(AbstractUser):
    """管理员表"""
    manager_name_validator = UnicodeUsernameValidator()
    # 用户名
    manager_name = models.CharField(max_length=30,
                                    unique=True,
                                    validators=[manager_name_validator, ],
                                    verbose_name=_('user name'),
                                    help_text=_(
                                        'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                    error_messages={
                                        # 字典结构的message
                                        # _适用于国际化的语言转换，会根据settings中设置的LANGUAGES自动转换
                                        # lang_zh_CN = gettext.translation(APP_NAME, LOCALE_DIR, ["zh_CN"])
                                        # lang_zh_CN.install()
                                        'unique': _("A manager with that username already exists."),
                                    },
                                    )
    # 密码
    password = models.CharField(verbose_name=_('password'), max_length=20)
    # 邮箱
    email = models.EmailField(verbose_name=_('Email name'), help_text=_('Please write your email'), blank=True)
    # 姓氏
    first_name = models.CharField(verbose_name=_('first name'), max_length=30, blank=True)
    # 名字
    last_name = models.CharField(verbose_name=_('last name'), max_length=150, blank=True)
    date_joined = models.DateTimeField(verbose_name=_('date joined'), default=timezone.now)
    # 设置认证标识，字段值必须唯一
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'manager_name'
    REQUIRED_FIELDS = ['email']

    sys_manager = UserManager()

    class Meta:
        verbose_name = _('manager')
        verbose_name_plural = _('managers')
'''


