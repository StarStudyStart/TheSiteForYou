# /bin/bash/python3
# -*- coding:utf8 -*-
# @Time: 2022/1/3 12:20
from django.urls import path, re_path, register_converter
from . import views, converts

# register_converter(converts.FilterConverts, 'filter')

app_name = 'blogs'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('up_or_down/', views.up_or_down, name='up_or_down'),  # up_or_down会被匹配成用户名，要放置到前面
    path('comment/', views.comment, name='comment'),
    # 后台管理
    path('backend/', views.backend, name='backend'),
    # 文章
    path('backend/new_blog/', views.new_blog, name='new_blog'),
    path('backend/edit_blog/<int:pk>/', views.edit_blog, name='edit_blog'),
    path('backend/delete_blog/<int:pk>/', views.delete_blog, name='delete_blog'),
    # 分类
    path('backend/new_category/', views.new_category, name='new_category'),
    path('backend/edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('backend/delete_category/<int:pk>/', views.delete_category, name='delete_category'),
    # 标签
    path('backend/new_tag/', views.new_tag, name='new_tag'),
    path('backend/edit_tag/<int:pk>/', views.edit_tag, name='edit_tag'),
    path('backend/delete_tag/<int:pk>/', views.delete_tag, name='delete_tag'),

    # 页面展示
    path('<str:username>/', views.user_site, name='user_site'),
    path('<str:username>/p/<int:pk>/', views.blog_details, name='detail'),
    re_path(r'^(?P<username>\w+)/(?P<flag>tag|category|archive)/(?P<param>.*)/$', views.user_site, name='filter'),

]
