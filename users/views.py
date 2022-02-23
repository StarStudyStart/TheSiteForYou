from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required

import random
import string
import logging

from users.forms import RegForm, LoginForm
from users.models import Author
from blogs.models import UserSite

from PIL import Image, ImageDraw, ImageFont

REDIRECT_FIELD_NAME = 'next'


# Create your views here.
def register(request):
    """用户注册"""
    if request.method == 'POST':
        register_form = RegForm(request.POST)
        if register_form.is_valid():
            clean_data = register_form.cleaned_data
            username = clean_data['username']
            avatar_obj = request.FILES.get('avatar', None)
            if avatar_obj:
                clean_data['avatar'] = avatar_obj
            clean_data.pop('confirm_password')
            user = Author.objects.create_user(**clean_data)
            # 注册用户时，自动创建站点  每个用户自动关联一个站点
            UserSite.objects.create(site_title='%s的个人博客' % username, site_name='',
                                    user=user)
            return HttpResponseRedirect(reverse('users:login'))
    else:
        register_form = RegForm()
    return render(request, 'users/register.html', context={'register_form': register_form})


def log_in(request):
    """用户登陆"""
    redirect_to = request.POST.get(
        REDIRECT_FIELD_NAME,
        request.GET.get(REDIRECT_FIELD_NAME, '')
    )
    # POST请求
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            row_code = request.session['code'].lower()
            input_code = request.POST['valid_code'].lower()
            # 验证码校验(忽略大小写)
            if input_code == row_code:
                clean_data = login_form.cleaned_data
                authenticate_user = authenticate(
                    request,
                    username=clean_data['username'],
                    password=clean_data['password']
                )
                if authenticate_user is not None and authenticate_user.is_active:
                    author = Author.objects.get(username=clean_data['username'])
                    login(request, author)
                    return HttpResponseRedirect(redirect_to)
                # 用户名或密码错误
                elif not authenticate_user:
                    login_form.add_error('password', '用户名或密码错误')
                # 用户未激活
                elif not authenticate_user.is_active:
                    login_form.add_error('username', '用户名被禁用')
            else:
                login_form.valid_error = '验证码错误，请重新输入!'
    # get请求
    else:
        login_form = LoginForm()

    if not redirect_to:
        redirect_to = reverse('blogs:home')
    return render(request, 'users/login.html', context={'login_form': login_form, 'next': redirect_to})


@login_required
def log_out(request):
    """用户登出"""
    logout(request)
    return HttpResponseRedirect(reverse('blogs:home'))


def get_code(request, refresh):
    """获取验证码图片"""
    # 图片对象->画布
    img_obj = Image.new('RGB', (550, 35), get_random())
    # 绘制图片的对象
    img_draw = ImageDraw.Draw(img_obj)
    code = ''
    # 随机绘制4个字符（大、小写字母，数字）
    for i in range(1, 5):
        random_int = random.choice(string.digits)
        random_upper = random.choice(string.ascii_uppercase)
        random_lower = random.choice(string.ascii_lowercase)
        per_code = random.choice([random_int, random_lower, random_upper])
        img_font = ImageFont.truetype('static/font/荆南麦圆体.ttf', 30)
        img_draw.text((i * 100, 0), per_code, font=img_font, spacing=4, align='center')
        code += per_code
    from io import BytesIO
    # 写入内存对象
    io_bytes = BytesIO()
    img_obj.save(io_bytes, 'png')

    # 存入session会话中便于校验
    request.session['code'] = code
    print(request.session['code'])
    return HttpResponse(io_bytes.getvalue())


def get_random():
    """返回随机背景颜色"""
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


@login_required
def set_pwd(request):
    """修改密码"""
    back_dic = {'code': 0, 'msg': ''}
    if request.is_ajax():
        if request.method == 'POST':
            old_password = request.POST['old_password']
            is_right = request.user.check_password(old_password)
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            if not new_password:
                back_dic['code'] = 1001
                back_dic['msg'] = '新密码不能为空'
            else:
                if new_password == confirm_password:
                    if is_right:
                        back_dic['code'] = 1000
                        request.user.set_password(new_password)
                        request.user.save()
                        back_dic['msg'] = '修改成功，请重新登录'
                    else:
                        back_dic['code'] = 1003
                        back_dic['msg'] = '原密码错误'
                else:
                    back_dic['code'] = 1002
                    back_dic['msg'] = '确认密码与新密码不一致'

    return JsonResponse(back_dic)
