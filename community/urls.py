from django.urls import path
from . import views

app_name = 'community'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.article_create, name='article_create'),
    path('<int:article_pk>/', views.article_RUD, name='article_RUD'),
    path('<int:article_pk>/like/', views.article_like, name='article_like'),
    path('<int:article_pk>/comments/', views.comment_CR, name='comment_CR'),
    path('<int:article_pk>/comments/all/', views.comment_ALL, name='comments_ALL'),
    path('<int:article_pk>/comments/<int:comment_pk>/', views.comment_UD, name='comment_UD'),
    path('<int:article_pk>/comments/<int:comment_pk>/like/', views.comment_like, name='comment_like'),
]