from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth.utils import OAuthQQ
# Create your views here.


# 接收请求并组织对应qq登陆url并返回给浏览器
# GET /oauth/qq/authorizations/?next=<登录成功跳转页面地址>  默认为首页,next参数不一定存在
class QQAuthURLView(APIView):
    def get(self, request):
        """
        获取QQ登陆网址
        1. 获取next参数
        2. 组织QQ登陆的网址和参数
        3. 返回QQ登陆网址
        """
        # 1. 获取next参数
        next = request.query_params.get('next', '/')  # None

        # 2.组织QQ登陆的网址和参数
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_login_url()

        # 3.返回QQ登陆网址
        return Response({'login_url': login_url})