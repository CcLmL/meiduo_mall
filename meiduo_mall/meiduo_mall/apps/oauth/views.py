from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import QQAuthUserSerializer
from oauth.utils import OAuthQQ
# Create your views here.


# GET /oauth/qq/user/?code=<code>
class QQAuthUserView(GenericAPIView):
    serializer_class = QQAuthUserSerializer

    def post(self, request):
        """
        保存绑定QQ登录用户的数据:
        1. 获取参数并进行校验(参数完整性，手机号格式，access_token是否有效，短信验证码是否正确)
        2. 保存绑定QQ登录用户的数据并签发jwt token
        3. 返回响应数据
        """
        # 1. 获取参数并进行校验(参数完整性，手机号格式，access_token是否有效，短信验证码是否正确)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 保存绑定QQ登陆用户的数据并签发jwt token(create)
        serializer.save()
        #  3.返回响应数据
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def get(self, request):
        """
        获取QQ登陆用户的openid并进行校验
        1. 获取code并进行校验(code必传)
        2. 获取QQ登陆用户的openid
            2.1 根据code请求QQ服务器获取access_token
            2.2 根据access_token请求QQ服务器获得openid
        3. 根据openid进行处理
            3.1 如果openid已经绑定过本网站用户,直接签发jwt token并返回
            3.2 如果openid未绑定过本网站用户,对openid进行加密,返回加密之后的内容
        """
        # 1. 获取code并进行校验(code必传)
        code = request.query_params.get('code')  # None

        if code is None:
            return Response({'message': '缺少code参数'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 获取QQ登陆用户的openid
        oauth = OAuthQQ()

        try:
            # 2.1 根据code请求QQ服务器获取access_token
            access_token = oauth.get_access_token(code)
            # 2.2 根据access_token请求QQ服务器获得openid
            openid = oauth.get_openid(access_token)
        except QQAPIError:
            return Response({'message': 'QQ登陆服务异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 3. 根据openid进行处理
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 3.2 如果openid未绑定过本网站用户,对openid进行加密,返回加密之后的内容
            access_token = OAuthQQ.generate_save_user_token(openid)
            return Response({'access_token': access_token})
        else:
            # 3.1 如果openid已经绑定过本网站用户,直接签发jwt token并返回
            user = qq_user.user

            # 有服务器生成一个jwt token数据,包含登陆用户身份信息
            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 生成载荷
            payload = jwt_payload_handler(user)
            # 生成jwt token
            token = jwt_encode_handler(payload)

            # 返回响应
            resp_data = {
                'user_id': user.id,
                'username': user.username,
                'token': token
            }
            return Response(resp_data)


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