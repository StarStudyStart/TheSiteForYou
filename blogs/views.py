from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from blogs.models import Blog, Comment, Category, Tag, UpAndDown, Tag4Blog
from blogs.forms import BlogForm, CategoryForm, TagForm
from users.models import Author

from datetime import datetime
import markdown
from distutils.util import strtobool


# Create your views here.

def home(request):
    """
    主页面
    展示所有blog（不区分用户）
    """
    user = request.user
    blog_queryset = Blog.objects.all().order_by('-create_time')
    return render(request, 'blogs/home.html', context={'user': user, 'blog_queryset': blog_queryset})


def user_site(request, username, **kwargs):
    """展示当前站点（用户）下所有文章"""
    user_obj = Author.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'blogs/404.html')
    # 一对一站点
    cur_user_site = user_obj.usersite
    blog_list = Blog.objects.filter(author__username=username)
    if kwargs:
        flag = kwargs.get('flag')
        param = kwargs.get('param')
        if flag == 'tag':
            blog_list = blog_list.filter(tags__id=param)
        elif flag == 'category':
            blog_list = blog_list.filter(category__id=param)
        elif flag == 'archive':
            _date = datetime.strptime(param, '%Y-%m')
            blog_list = blog_list.filter(create_time__year=_date.year, create_time__month=_date.month)
        else:
            redirect('blogs:home')

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
    return render(request, 'blogs/user_site.html', context=locals())


def blog_details(request, username, pk):
    """blog内容明细展示"""

    blog = Blog.objects.filter(pk=pk, author__username=username).first()
    if not blog:
        return render(request, 'blogs/404.html')
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    blog.content = md.convert(blog.content)

    # 评论展示
    comment_list = Comment.objects.filter(blog=blog)
    # for comment_obj in Comment.objects.filter(blog=blog):
    #     parent_id = comment_obj.parent_id
    #     if parent_id is not None:
    #         parent_obj = Comment.objects.get(pk=parent_id)
    #         parent_obj.child_cm = comment_obj
    #         comment_list.append(parent_obj)
    #     else:
    #         comment_list.append(comment_obj)
    context = {
        'username': username,
        'blog_id': pk,
        'blog': blog,
        'toc': md.toc,
        'comment_list': comment_list,
    }
    return render(request, 'blogs/blog_details.html', context=context)


def up_or_down(request):
    """
    blog内容中的：点赞点踩逻辑
        # 1. 判断用户是否登陆
        # 2. 判断用户是否给自己的文章点赞
        # 3. 判断是否已经点过赞
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 是否登录
        blog_id = request.POST['blog_id']
        blog = Blog.objects.get(pk=blog_id)
        if request.user.is_authenticated:
            is_up = bool(strtobool(request.POST['is_up']))
            # 是否本人点赞
            if request.user != blog.author:
                is_already_click = UpAndDown.objects.filter(user=request.user, blog=blog)
                if not is_already_click:
                    if is_up:
                        Blog.objects.filter(pk=blog_id).update(up_num=F('up_num') + 1)
                        back_dic['code'] = 1001
                        back_dic['msg'] = '点赞成功'
                    else:
                        Blog.objects.filter(pk=blog_id).update(down_num=F('down_num') + 1)
                        back_dic['code'] = 1002
                        back_dic['msg'] = '点踩成功'
                    UpAndDown.objects.create(user=request.user, blog=blog, is_up=is_up)
                # 已经点过赞/踩
                else:
                    back_dic['msg'] = '不可重复操作'
                    back_dic['code'] = 1003
            # 给自己的文章点赞
            else:
                back_dic['msg'] = '不能给自己的文章点赞/踩ooo'
                back_dic['code'] = 1004
        else:
            back_dic['msg'] = '用户未登录，<a href=/users/login/?next=/{}/p/{}>请登录</a>'.format(blog.author, blog_id)
            back_dic['code'] = 1005
        return JsonResponse(back_dic)
    else:
        return HttpResponse("wrong number: 500")


def comment(request):
    """blog明细中的评论逻辑"""
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.user.is_authenticated:
            blog_id = request.POST['blog_id']
            parent_id = request.POST['parentId']
            cm_content = request.POST['cm_content']
            with transaction.atomic():
                Blog.objects.filter(pk=blog_id).update(comment_num=F('comment_num') + 1)
                blog_obj = Blog.objects.get(pk=blog_id)
                cm_obj = Comment.objects.create(comment_user=request.user, blog_id=blog_id, content=cm_content,
                                                parent_id=parent_id)
            tmp_render = '<li class="list-group-item">\
                        <p class="list-group-item-heading" style="padding:8xp;padding-right:7px">\
                            <span style="margin-left:5px">{}</span>\
                            <span style="margin-left:5px">{}</span>\
                            <span class="pull-right reply"><a href="#id_comment">回复</a></span>\
                        </p>\
                        <h4 class="list-group-item-text">{}</h4>\
                    </li>'
            back_dic['code'] = 1000
            back_dic['msg'] = '<p style="color:#337ab7"><br>评论成功!!<br></p> %s' % tmp_render.format(cm_obj.comment_time,
                                                                                                   cm_obj.comment_user,
                                                                                                   cm_content)
            if parent_id:
                back_dic['msg'] = '<p style="color:#337ab7"><br>评论成功!!<br></p> %s' % tmp_render.format(
                    '@%s' % cm_obj.parent.comment_user.username, cm_obj.comment_time, cm_obj.comment_user, cm_content)
        else:
            back_dic['code'] = 1001
            back_dic['msg'] = '用户未登录'
        return JsonResponse(back_dic)


@login_required
def backend(request):
    """后台管理页面"""
    blog_list = Blog.objects.filter(author=request.user)
    tag_list = Tag.objects.filter(user_site=request.user.usersite)
    category_list = Category.objects.filter(user_site=request.user.usersite)
    context = {
        'user': request.user,
        'blog_list': blog_list,
        'tag_list': tag_list,
        'category_list': category_list,
    }
    return render(request, 'blogs/backend/backend.html', context=context)


@login_required
def new_blog(request):
    """添加新文章"""
    if request.method == 'GET':
        blog_form = BlogForm()
    else:
        blog_form = BlogForm(request.POST)
        if blog_form.is_valid():
            clean_data = blog_form.cleaned_data
            category_id = request.POST['category']
            tag_ids = request.POST.getlist('tag')
            _blog = Blog.objects.create(
                title=clean_data['title'],
                content=clean_data['content'],
                excerpt=clean_data['excerpt'],
                cover=clean_data['cover'],
                user_site=request.user.usersite,
                author=request.user,
                category_id=category_id
            )
            tag_blog_list = [Tag4Blog(blog=_blog, tag_id=_id) for _id in tag_ids]
            Tag4Blog.objects.bulk_create(tag_blog_list)
            return redirect(reverse('blogs:backend'))

    # 过滤当前用户站点下的标签、分类
    tag_list = Tag.objects.filter(user_site__user=request.user)
    category_list = Category.objects.filter(user_site__user=request.user)
    context = {
        'user': request.user,
        'form': blog_form,
        'tag_list': tag_list,
        'category_list': category_list,
    }
    return render(request, 'blogs/backend/new_blog.html', context)


@login_required
def edit_blog(request, pk):
    """编辑/更新新文章"""
    blog_obj = Blog.objects.get(pk=pk)

    # 如果获取不到blog对象/不是文章作者本人，则返回404
    if not blog_obj or blog_obj.author != request.user:
        return render(request, 'blogs/404.html')
    # 处理请求
    if request.method == 'GET':
        blog_form = BlogForm(instance=blog_obj)
    else:
        blog_form = BlogForm(instance=blog_obj, data=request.POST)
        if blog_form.is_valid():
            category_id = request.POST['category']
            tag_ids = request.POST.getlist('tag')
            blog_edited = blog_form.save(commit=False)
            # 更新分类信息
            blog_edited.category_id = category_id
            blog_edited.save()

            # 先删除blog_id所有的tag，再重新添加
            Tag4Blog.objects.filter(blog_id=pk).delete()
            tag_blog_list = [Tag4Blog(blog_id=pk, tag_id=_id) for _id in tag_ids]
            Tag4Blog.objects.bulk_create(tag_blog_list)

            return redirect(reverse('blogs:backend'))
    selected_category = Category.objects.get(pk=blog_obj.category_id)
    selected_tag4blogs = Tag4Blog.objects.filter(blog_id=pk)
    tag_list = Tag.objects.filter(user_site__user=request.user)
    category_list = Category.objects.filter(user_site__user=request.user)
    context = {
        'selected_category': selected_category,
        'selected_tag4blogs': selected_tag4blogs,
        'form': blog_form,
        'blog_id': pk,
        'tag_list': tag_list,
        'category_list': category_list,
    }
    return render(request, 'blogs/backend/edit_blog.html', context=context)


@login_required
def delete_blog(request, pk):
    """删除文章"""
    blog_obj = Blog.objects.get(pk=pk)

    # 如果获取不到blog对象/不是文章作者本人，则返回404
    if not blog_obj or blog_obj.author != request.user:
        return render(request, 'blogs/404.html')
    # 删除blog
    blog_obj.delete()
    # 删除标签
    Tag4Blog.objects.filter(blog_id=pk).delete()

    return redirect(reverse("blogs:backend"))


@login_required
def edit_category(request, pk):
    """编辑分类"""
    category_obj = Category.objects.get(pk=pk)

    # 如果获取不到，则返回404
    if not category_obj:
        return render(request, 'blogs/404.html')
    if request.method == "GET":
        form = CategoryForm(instance=category_obj)
    else:
        form = CategoryForm(instance=category_obj, data=request.POST)
        modified_obj = form.save(commit=False)
        modified_obj.user_site = request.user.usersite
        modified_obj.save()
        return redirect(reverse("blogs:backend"))

    return render(request, 'blogs/backend/edit_category.html', {'form': form, 'category_id': pk})


@login_required
def new_category(request):
    """新增分类"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_obj = form.save(commit=False)
            #  别忘记加上站点字段
            category_obj.user_site = request.user.usersite
            category_obj.save()
            return redirect(reverse('blogs:backend'))  # 待优化 跳转到对应标签选项卡（前端使用ajax发送请求）
    else:
        form = CategoryForm()
    context = {
        'form': form
    }
    return render(request, 'blogs/backend/new_category.html', context)


@login_required
def delete_category(request, pk):
    """删除分类"""
    category_obj = Category.objects.get(pk=pk)
    if not category_obj:
        return render(request, 'blogs/404.html')
    category_obj.delete()
    return redirect(reverse("blogs:backend"))


@login_required
def edit_tag(request, pk):
    """编辑标签"""
    tag_obj = Tag.objects.get(pk=pk)

    # 如果获取不到，则返回404
    if not tag_obj:
        return render(request, 'blogs/404.html')
    if request.method == "GET":
        form = TagForm(instance=tag_obj)
    else:
        form = TagForm(instance=tag_obj, data=request.POST)
        modified_obj = form.save(commit=False)
        modified_obj.user_site = request.user.usersite
        modified_obj.save()
        return redirect(reverse("blogs:backend"))

    return render(request, 'blogs/backend/edit_tag.html', {'form': form, 'tag_id': pk})


@login_required
def new_tag(request):
    """新增标签"""
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag_obj = form.save(commit=False)
            #  别忘记加上站点字段
            tag_obj.user_site = request.user.usersite
            tag_obj.save()
            return redirect(reverse('blogs:backend'))  # 待优化 跳转到对应标签选项卡（前端使用ajax发送请求）
    else:
        form = TagForm()
    context = {
        'form': form
    }
    return render(request, 'blogs/backend/new_tag.html', context)


@login_required
def delete_tag(request, pk):
    """删除标签内容"""
    tag_obj = Tag.objects.get(pk=pk)
    if not tag_obj:
        return render(request, 'blogs/404.html')
    tag_obj.delete()
    return redirect(reverse("blogs:backend"))
