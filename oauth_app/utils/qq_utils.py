# -*- coding: utf-8 -*-
# @Time  : 2020/11/21 上午12:00
# @Author : 司云中
# @File : qq_utils.py
# @Software: Pycharm

from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from django.conf import settings
import json

from Emall.loggings import Logging
from oauth_app.utils.exceptions import QQServiceUnavailable

common_logger = Logging.logger('django')


class OAuthQQ(object):
    """
    QQ认证授权辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE

    def generate_qq_login_url(self):
        """
        生成qq登录的网址
        :return: url
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """
        获取access_token
        :param code: qq提供的code.10分钟过期
        :return: access_token
        """
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'fmt': 'json'
        }
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        response = urlopen(url)
        response_data = response.read().decode()
        data = parse_qs(response_data)  # 返回字典格式
        access_token = data.get('access_token', None)
        if not access_token:
            raise QQServiceUnavailable()
        return access_token[0]

    @staticmethod
    def get_openid(access_token):
        """
        携带access_token获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        response_data = response.read().decode()
        try:
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            raise QQServiceUnavailable(data)
        openid = data.get('openid', None)
        return openid
