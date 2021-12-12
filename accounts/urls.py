from django.urls import path
from . import views
from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    path('signup/', views.signup),
    path('api-token-auth/', obtain_jwt_token),
    path('<username>/', views.user_manage),
    path('<username>/follow/', views.follow),
    path('<username>/profileImg/', views.set_profile_img),
    path('<username>/movies/', views.get_user_movies),
    path('<username>/reviews', views.get_user_reviews),
]
