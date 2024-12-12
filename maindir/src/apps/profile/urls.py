from django.urls import path
from .views import profile, profile_edit, activate, profile_email_for_verify, verify_done

urlpatterns = [
    path('profile/verify/', profile_email_for_verify, name='profile_email_for_verify'),
    path('profile/verify/done/', verify_done, name='verify_done'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('activate/<uidb64>/<token>/<email>/', activate, name='activate'),
]