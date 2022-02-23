from django.contrib import admin
from blogs.models import UpAndDown, Category, Comment, Blog, UserSite, Tag, Tag4Blog
from users.models import Author
# Register your models here.
admin.site.register(UpAndDown)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Blog)
admin.site.register(UserSite)
admin.site.register(Tag)
admin.site.register(Author)
admin.site.register(Tag4Blog)
