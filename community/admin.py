from django.contrib import admin
from .models import Article, Article_Comment

# Register your models here.
# 명세에는 없으므로 추후에 제거
admin.site.register(Article)
admin.site.register(Article_Comment)