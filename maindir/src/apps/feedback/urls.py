from django.urls import path

from .views import feedback_create_view
urlpatterns = [
    path('feedback/', feedback_create_view, name='feedback'),
]