# -*- coding: utf-8 -*-
# @Time  : 2020/11/20 下午11:57
# @Author : 司云中
# @File : qq_api.py
# @Software: Pycharm

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from oauth_app.utils.qq_utils import OAuthQQ


class QQOauthUrl(GenericAPIView):
    """
    QQ登录操作类之获取提供用于登录的QQ
    """

    def get(self, request):
        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.generate_qq_login_url()
        return Response({'login_url':login_url})

class QQOauthAccessToken(GenericAPIView):
    """
    携带code和state回调该视图
    请求qq服务器获取access token
    """