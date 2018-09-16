from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    """用户模型类"""
    # 因为Django框架自带用户认证类,所以我们只需要继承对应类并添加自己的设置就可以了
    mobile = models.CharField(max_length=11, verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name