from django.db import models
from mdeditor.fields import MDTextField


# Create your models here.
class UserSite(models.Model):
    """个人站点表"""
    site_title = models.CharField(verbose_name='站点标题', max_length=32)
    site_name = models.CharField(verbose_name='站点名称', max_length=32)
    site_theme = models.TextField(verbose_name='站点样式表', blank=True, null=True, max_length=64)  # 存储css样式

    user = models.OneToOneField(to='users.Author', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.site_title


class Category(models.Model):
    """分类表"""
    name = models.CharField(max_length=20, verbose_name="分类名")
    user_site = models.ForeignKey(to='UserSite', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """标签表"""
    name = models.CharField(max_length=20, verbose_name="标签名")
    user_site = models.ForeignKey(to='UserSite', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Blog(models.Model):
    """
    Blog内容表
    """
    title = models.CharField(max_length=64, verbose_name='标题')
    excerpt = models.CharField(max_length=255, blank=True, null=True, verbose_name='摘要')
    content = MDTextField(verbose_name='内容')

    create_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    cover = models.ImageField(blank=True, null=True, verbose_name='封面')

    user_site = models.ForeignKey(to='UserSite', on_delete=models.CASCADE)
    author = models.ForeignKey('users.Author', null=True, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey('Category', null=True, on_delete=models.SET_NULL, verbose_name='分类')
    tags = models.ManyToManyField('Tag', through='Tag4Blog', through_fields=('blog', 'tag'), verbose_name='标签')

    up_num = models.BigIntegerField(default=0, verbose_name='点赞数')
    down_num = models.BigIntegerField(default=0, verbose_name='点踩数')
    comment_num = models.BigIntegerField(default=0, verbose_name='评论数')

    def __str__(self):
        return self.title


class Tag4Blog(models.Model):
    """
    tag 中间表
    所有数据外键都是级联删除，没有单独存在的必要
    """
    tag = models.ForeignKey(to='Tag', on_delete=models.CASCADE)
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE)


class Comment(models.Model):
    """
    评论表：自关联
    """
    comment_user = models.ForeignKey(to='users.Author', on_delete=models.CASCADE, null=True, verbose_name="评论人")
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE, verbose_name="评论文章")
    content = models.CharField(max_length=255, verbose_name='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='根评论')

    def __str__(self):
        return self.content


class UpAndDown(models.Model):
    """点赞点踩表"""
    user = models.ForeignKey(to='users.Author', on_delete=models.CASCADE)
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE)
    is_up = models.BooleanField()
