from django.db import models


# Create your models here.
class BaseModel(models.Model):
    """抽象模型基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 指定该模型类是一个抽象抽象模型类,在进行迁移时不生成表
        abstract = True