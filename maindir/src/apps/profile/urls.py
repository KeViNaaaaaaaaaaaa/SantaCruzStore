from django.urls import path
from .views import profile, profile_edit, activate, profile_email_for_verify, verify_done, order_detail, order_delete, profile_delete

urlpatterns = [
    path('profile/verify/', profile_email_for_verify, name='profile_email_for_verify'),
    path('profile/verify/done/', verify_done, name='verify_done'),
    path('profile/', profile, name='profile'),
    path('profile/delete/', profile_delete, name='profile_delete'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('activate/<uidb64>/<token>/<email>/', activate, name='activate'),
    path('profile/<int:order_id>/', order_detail, name='order_detail'),
    path('profile/<int:order_id>/delete/', order_delete, name='order_delete'),
]