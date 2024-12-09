from django.contrib.auth.views import LoginView
from django.urls import path
from api.auth.views import register, user_login, profile, logout_user, force_logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('profile/', profile, name='profile'),
    path('logout/', logout_user, name='logout'),
]