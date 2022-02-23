# /bin/bash/python3
# -*- coding:utf8 -*-
# @Time: 2022/1/16 22:48
from django import template
from blogs.models import Category, Tag, Blog
from users.models import Author

from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


@register.inclusion_tag('blogs/left_menu.html')
def left_menu(username):
    user_obj = Author.objects.filter(username=username).first()
    if not user_obj:
        return None
    cur_user_site = user_obj.usersite
    # 分类筛选
    category_list = Category.objects.filter(
        user_site=cur_user_site).annotate(count_num=Count('blog__pk')).values_list('name', 'count_num', 'pk')
    # 标签筛选 （标签名，基数值）
    tag_list = Tag.objects.filter(user_site=cur_user_site).annotate(
        count_num=Count('blog__pk')).values_list('name', 'count_num', 'pk')
    # 日期筛选（按月筛选）
    date_list = Blog.objects.filter(user_site=cur_user_site).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(
        c=Count('pk')).values_list('month', 'c')
    context = {
        'category_list': category_list,
        'tag_list': tag_list,
        'date_list': date_list,
        'user_obj': user_obj,
    }
    return context
