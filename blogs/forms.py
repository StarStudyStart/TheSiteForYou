# /bin/bash/python3
# -*- coding:utf8 -*-
# @Time: 2022/1/22 22:42
from django import forms
from blogs import models
from mdeditor.widgets import MDEditorWidget


class BlogForm(forms.ModelForm):
    class Meta:
        model = models.Blog
        fields = ['title', 'excerpt', 'content', 'cover']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.TextInput(attrs={'class': 'form-control'}),
            'content': MDEditorWidget(attrs={'class': 'pull-left'}),
            'cover': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.RadioSelect(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    """分类表单"""

    class Meta:
        model = models.Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


class TagForm(forms.ModelForm):
    """标签表单"""

    class Meta:
        model = models.Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
