from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
def user_dir_path(instance, filename):
    return 'user_{0}/avatar/{1}'.format(instance.username, filename)


class Author(AbstractUser):
    """作者：用户名表"""
    link = models.CharField(verbose_name='联系方式', max_length=32, null=True)
    create_time = models.DateField(auto_now_add=True)
    avatar = models.FileField(upload_to=user_dir_path, default='uploads/avatar/default.jpg')

    def __str__(self):
        return self.username
