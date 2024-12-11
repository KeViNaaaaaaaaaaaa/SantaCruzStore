from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from apps.profile.views import profile, profile_edit

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
]