from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from users.serializers import CreateUserSerializer
from users.models import User
from rest_framework.views import APIView
# Create your views here.


# POST /users/
# class UserVIew(GenericAPIView):
class UserVIew(CreateAPIView):  # 继承了mixins.CreateModelMixin(封装了post方法用于create),GenericAPIView
    # 指定当前视图使用的序列化器类
    serializer_class = CreateUserSerializer

    # def post(self, request):
    #     """
    #     注册用户信息的保存:
    #     1. 获取参数并校验(参数完整性, 是否同意协议, 手机号格式, 手机号是否已经注册, 短信验证码是否正确)
    #     2. 保存注册用户的信息
    #     3. 返回注册用户数据
    #     """
    #     # 1. 获取参数并校验(参数完整性, 是否同意协议, 手机号格式, 手机号是否已经注册, 短信验证码是否正确)
    #     serializer = self.get_serializer(data=request.data)
    #
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 保存注册用户的信息(create)
    #     serializer.save()
    #
    #     # 3. 返回注册用户数据
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# url(r'^usernames/(?P<username>\w{5,20})/count/$'
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)