from django.db import models

from meiduo_mall.utils.models import BaseModel
# Create your models here.


class OAuthQQUser(BaseModel):
    """QQ登录用户信息模型类"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='OpenID', db_index=True)  # 为openid这个字段建立索引,方便以后我们要
    # 通过这个字段去查找数据,可以增加查询效率

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name