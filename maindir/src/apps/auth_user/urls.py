from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from apps.auth_user.views import register, user_login, logout_user, google_login

urlpatterns = [
    path('accounts/email/', google_login, name='jwtgoogle'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', logout_user, name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]