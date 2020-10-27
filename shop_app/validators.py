from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class CommodityValidator(validators.RegexValidator):
    """验证商品名称"""
    regex = '^[\u4e00-\u9fa5]{0,20}$|\w{0,30}$'
    message = _('商品名称需在20个汉子内或30个字母或数字内')
    flags = 0

    def __init__(self, regex=regex, message=message, code=None, inverse_match=None, flags=flags):
        super().__init__(regex, message, flags)
