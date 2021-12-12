from django.contrib import admin
from .models import Movie
from .models import Genre_Score, Review, Review_Comment
# Register your models here.

admin.site.register(Movie)
# 명세에는 없으므로 추후에 제거
admin.site.register(Genre_Score)
admin.site.register(Review)
admin.site.register(Review_Comment)

