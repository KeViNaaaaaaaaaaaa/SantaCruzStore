from django.urls import path, include
from .views import admin_analytics, user_analytics


urlpatterns = [
    path('', admin_analytics, name='admin_analytics'),
    path('user/<int:user_id>/', user_analytics, name='user_analytics'),
]