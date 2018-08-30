from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Users(AbstractUser):
    """自定义用户模型类/继承系统模型类并添加自定义字段"""

    # 新增用户手机字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    # 自定义表明及声明文字
    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
