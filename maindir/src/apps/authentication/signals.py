from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from apps.authentication.views import user_login

@receiver(user_logged_in)
def auto_login_after_google_signup(sender, request, user, **kwargs):
    user_login(request)