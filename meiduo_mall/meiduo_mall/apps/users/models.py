from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import JSONWebSignatureSerializer as JWSSerializer

# Create your models here.
from django.conf import settings  # 使用我们配置文件dev中的数据可以直接导入这个模块

from users import constants


class User(AbstractUser):
    """用户模型类"""
    # 因为Django框架自带用户认证类,所以我们只需要继承对应类并添加自己的设置就可以了
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # openid = models.CharField(max_length=64, verbose_name='OpenID')  # 因为一个用户可以对应多个QQ账户,所以在这里设置openid并不能实现一对多
    # 所以要建立一个单独的表

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """
        生成对应用户的邮箱验证的连接地址
        """
        # 组织用户数据
        data ={
            'id': self.id,
            'email': self.eamil
        }

        # 进行加密
        serializer = JWSSerializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        token = serializer.dumps(data).decode()

        # 拼接验证的连接地址
        verify_url = 'http://www.meiduo.site:8000/success_verify_email.html?token=' + token

        return verify_url
