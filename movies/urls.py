from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    # path('actors/', views.actor_list),
    path('r6/', views.movie_list_r6),
    path('t20/', views.movie_list_t20),
    path('genres/', views.genre_list),
    path('score/', views.get_genre_score),
    path('personal_curation/', views.personal_curation),
    path('search/title/<query>/', views.search_by_title),
    path('search/genre/<query>/', views.search_by_genre),
    path('<int:movie_pk>/', views.movie_detail),
    path('<int:movie_pk>/actors/', views.actor_list_by_movie),
    path('<int:movie_pk>/wish/', views.movie_wish),
    path('<int:movie_pk>/like/', views.movie_like),
    path('<int:movie_pk>/like/score/', views.genre_score),
    path('<int:movie_pk>/review/', views.movie_review_CR),
    path('<int:movie_pk>/review/all/', views.movie_review_all),
    path('<int:movie_pk>/review/<int:review_pk>/', views.movie_review_UD),
    path('<int:movie_pk>/review/<int:review_pk>/like/', views.movie_review_like),
    path('<int:review_pk>/comment/', views.review_comment_CR),
    path('<int:review_pk>/comment/all/', views.review_comment_all),
    path('<int:review_pk>/comment/<int:comment_pk>/', views.review_comment_UD),
    path('<int:review_pk>/comment/<int:comment_pk>/like/', views.review_comment_like),
    # path('review/', views.review_list),
    # path('review/<int:review_pk>/', views.review_detail),
]