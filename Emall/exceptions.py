# -*- coding: utf-8 -*-
# @Time  : 2021/1/1 下午7:46
# @Author : 司云中
# @File : exceptions.py
# @Software: Pycharm
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _

class ESConnectError(APIException):
    """ES连接出错"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('ES服务连接超时')
    default_code = 'ES Connection Error'


class AuthenticationError(APIException):
    """jwt校验错误"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('身份校验错误')
    default_code = 'Authentication Failed'


class LabelError(APIException):
    """标签格式错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('标签格式错误')
    default_code = 'Label Error'

class DataTypeError(APIException):
    """数据类型错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('数据类型错误')
    default_code = 'Params Type Error'


class DataFormatError(APIException):
    """数据格式非法"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('数据格式非法')
    default_code = 'Data Format Error'


class UserForbiddenError(APIException):
    """用户禁止登录"""
    status_code = status.HTTP_200_OK
    default_detail = _('用户无登录权限')
    default_code = 'Login Forbidden'


class UniversalServerError(APIException):
    """服务器通用错误"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('服务器处理产生错误')
    default_code = 'Server Error'


class SqlServerError(APIException):
    """数据库错误"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('数据不匹配')
    default_code = 'SQL Server Error'


class OldPasswordError(APIException):
    """旧密码错误"""
    status_code = status.HTTP_200_OK
    default_detail = _('旧密码错误')
    default_code = 'Old Password Error'


class NoBindPhone(APIException):
    """尚未绑定手机号异常"""
    status_code = status.HTTP_200_OK
    default_detail = _('用户尚未绑定手机号')
    default_code = 'No Bind Phone'


class NoBindEmail(APIException):
    """尚未绑定邮箱号"""
    status_code = status.HTTP_200_OK
    default_detail = _('用户尚未绑定邮箱号')
    default_code = 'No Bind Email'


class UserNotExists(APIException):
    """用户不存在异常"""
    status_code = status.HTTP_200_OK
    default_detail = _('用户不存在')
    default_code = 'User Not Exists'


class UserExists(APIException):
    """用户存在异常"""
    status_code = status.HTTP_200_OK
    default_detail = _('用户已存在')
    default_code = 'User has existed'


class UserTimesLimit(APIException):
    """用户限流"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _('请求超过限制')
    default_code = 'Request exceed limit'


class ThirdServiceBase(APIException):
    """第三方服务异常基类"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('服务异常')
    default_code = 'Service Support Error'


class EmailHasBeenBoundError(APIException):
    """邮件已经绑定"""
    status_code = status.HTTP_200_OK
    default_detail = _('邮件已经绑定')
    default_code = 'Emailed has been bound'


class PhoneHasBeenBoundError(APIException):
    """手机已经绑定"""
    status_code = status.HTTP_200_OK
    default_detail = _('手机已经绑定')
    default_code = 'Phone has been bound'


class CodeError(APIException):
    """验证码校验错误"""
    status_code = status.HTTP_200_OK
    default_detail = _('验证码校验错误')
    default_code = 'Code Validate Error'


class QQServiceError(ThirdServiceBase):
    """QQ第三方服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('QQ服务提供存在异常')
    default_code = 'QQ Service Error'


class WeiBoServiceError(ThirdServiceBase):
    """微博第三方服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('微博第三方服务存在异常')
    default_code = 'WeiBo Service Error'


class CodeServerError(ThirdServiceBase):
    """sms服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('短信验证码提供异常')
    default_code = 'SMS Error'


class OSSError(ThirdServiceBase):
    """OSS服务异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('OSS服务异常')
    default_code = 'OSS Error'


class IdentifyError(ThirdServiceBase):
    """身份证识别异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('身份校验服务异常')
    default_code = 'OCR Error'


class IdentifyExistError(APIException):
    """身份证已经被校验过"""
    status_code = status.HTTP_200_OK
    default_detail = _('身份证已经被校验过')
    default_code = 'OCR has been validated'


class AddressError(ThirdServiceBase):
    """地址存在异常"""
    status_code = status.HTTP_200_OK
    default_detail = _('地址操作存在异常')
    default_code = 'Address Error'


class FileError(APIException):
    """文件操作错误"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('文件操作异常')
    default_code = 'File Operation Error'


class FileExistedException(FileError):
    """文件已经存在"""
    pass


class UploadFileOSSError(FileError):
    """文件上传失败"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('文件上传异常')
    default_code = 'File Upload Error'


class DeleteFileOSSError(FileError):
    """删除文件失败"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('删除文件失败')
    default_code = 'File Delete Error'


class ModifyFileOSSError(FileError):
    """修改文件异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('修改文件失败')
    default_code = 'File Modify Error'


class DownLoadOSSError(FileError):
    """获取文件异常"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('获取文件失败')
    default_code = 'Retrieve File Error'


class RedisOperationError(APIException):
    """Redis服务错误"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('内存数据库异常')
    default_code = 'Redis Error'


class TypeTransformError(APIException):
    """数据类型转换异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('类型错误')
    default_code = 'Type Error'
