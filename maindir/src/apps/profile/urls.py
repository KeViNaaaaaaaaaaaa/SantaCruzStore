from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from apps.profile.views import profile, profile_edit, activate, send_activation_email

urlpatterns = [
    path('profile/verify/', send_activation_email, name='send_activation_email'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    re_path(r'^confirm-email/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', activate, name='confirm_email'),
]