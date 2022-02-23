# /bin/bash/python3
# -*- coding:utf8 -*-
# @Time: 2022/1/3 15:48
from django import forms
from users.models import Author


class RegForm(forms.Form):
    """用户注册表单"""
    username = forms.CharField(
        label='用户名',
        min_length=3,
        max_length=8,
        error_messages={
            'required': '用户名不能为空',
            'min_length': '用户名不能少于3位',
            'max_length': '用户名不能大于8位'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '用户名'
        }),
        help_text=['必填；', '用户名不得重名。']
    )
    password = forms.CharField(
        label='密码',
        min_length=3,
        max_length=20,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码不能少于3位',
            'max_length': '密码不能大于20位'
        },
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}),
        help_text=['你的密码必须包含至少 3 个字符；', '你的密码必须包含不能大于 20 个字符。']
    )
    confirm_password = forms.CharField(
        label='确认密码',
        min_length=3,
        max_length=20,
        error_messages={
            'required': '请输入与上面相同的密码',
        },
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码确认'}),
        help_text=['为了校验，请输入与上面相同的密码。']
    )
    link = forms.EmailField(
        label='邮箱',
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '无效的邮箱格式'
        },
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱'}),
        help_text=['邮箱不能为空。']
    )

    # avatar = forms.ImageField(
    #     label='头像'
    # )

    def clean_username(self):
        """校验用户名是否存在"""
        username = self.cleaned_data.get("username")
        is_exist = Author.objects.filter(username=username)
        if is_exist:
            self.add_error('username', '用户名已存在')
        return username

    def clean(self):
        """全局校验"""
        password = self.cleaned_data.get("password")
        confirm_pwd = self.cleaned_data.get("confirm_password")
        if password != confirm_pwd:
            self.add_error('confirm_password', '两次输入的密码不一致')
        return self.cleaned_data


class LoginForm(forms.Form):
    """用户登陆表单"""
    username = forms.CharField(
        label='用户名',
        min_length=3,
        max_length=8,
        error_messages={
            'required': '用户名不能为空',
            'min_length': '用户名不能少于3位',
            'max_length': '用户名不能大于8位'
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '用户名'
        }),
    )
    password = forms.CharField(
        label='密码',
        min_length=3,
        max_length=20,
        error_messages={
            'required': '密码不能为空',
        },
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}),
    )

    def clean_username(self):
        """校验用户名是否存在"""
        username = self.cleaned_data.get("username")
        is_exist = Author.objects.filter(username=username)
        if not is_exist:
            self.add_error('username', '用户名不存在，请前往注册')
        return username
