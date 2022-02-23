# /bin/bash/python3
# -*- coding:utf8 -*-
# @Time: 2022/1/3 18:18
from django.urls import path
from users import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('get_code/<int:refresh>', views.get_code, name='get_code'),
    path('set_pwd/', views.set_pwd, name='set_pwd'),
]
