from django.urls import path, include
from .views import admin_analytics, user_analytics, user_list


urlpatterns = [
    path('', admin_analytics, name='admin_analytics'),
    path('users/', user_list, name='user_list'),
    path('user/<int:user_id>/', user_analytics, name='user_analytics'),
]