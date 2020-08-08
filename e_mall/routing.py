# -*- coding: utf-8 -*-
# @Time  : 2020/8/8 下午4:09
# @Author : 司云中
# @File : routing.py
# @Software: Pycharm


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack, AuthMiddleware
from Propel_app import routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    # 下面跟着不同协议路由,可以支持多个协议
    'websocket': AuthMiddlewareStack(
        URLRouter(
            # chat_routing.websocket_urlpatterns,
            # 这里的路由路径只能有一个
            routing.websocket_urlpatterns,
        )
    ),
})
