from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers import CreateUserSerializer, UserDetailSerializer
from users.models import User
from rest_framework.views import APIView
# Create your views here.


# PUT/email/
class EmailView(GenericAPIView):
    # 指定当前视图所使用的权限控制类
    permission_classes = [IsAuthenticated]
    # serializer_class = EmailSerializer

    def get_object(self):
        """获取登陆用户"""
        # self.request: 视图的request对象
        return self.request.user

    def put(self, request):
        """
        登陆用户邮箱的设置:
        1. 获取登陆用户user
        2. 获取参数email并进行校验(email必传,邮箱格式)
        3. 设置user用户的邮箱并发送邮箱验证邮件
        4. 返回应答
        """
        # 1. 获取登陆用户user
        user = self.get_object()

        # 2. 获取参数email并进行校验(email必传,邮箱格式)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        # 3. 设置user用户的邮箱并发送邮箱验证邮件
        serializer.save()

        # 4.返回应答
        return Response(serializer.data)


# 用户个人信息页面
# class UserDetailView(GenericAPIView):
class UserDetailView(RetrieveAPIView):
    # 指定当前视图所使用的权限控制类
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):  # 重写序列化器中的方法
        """获取登陆用户"""
        # self.request: 视图的request对象(即使没有传递request参数也可以通过这个方法获得)
        return self.request.user

    # def get(self, request):
    #     """
    #     获取登陆用户的信息
    #     1. 获取登陆用户user
    #     2. 将用户的信息序列化并返回
    #     """
    #     # 1. 获取登陆用户user
    #     # user = request.user  # 能进入接口的user都是已经经过认证的
    #     user = self.get_object()
    #
    #     # 2. 将用户的信息序列化并返回
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data)


# 用户注册视图
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