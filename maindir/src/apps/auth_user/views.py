from datetime import timedelta

from django.contrib.auth.models import User
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from utils.helpers import create_jwt, decode_jwt
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib import messages

from apps.auth_user .forms import LoginForm, UserRegistrationForm

from apps.profile.models import Profile

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required

from django.utils import timezone


def logout_user(request):
    logout(request)
    request.session.flush()
    response = render(request, 'logout.html', {'message': 'Logged out successfully'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def register(request):
    user_form = UserRegistrationForm()
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                return render(request, 'register.html', {'user_form': user_form, 'error': 'Username already taken'})

            user = User.objects.create_user(username=username, password=password)
            profile = Profile.objects.create(user=user)
            profile.save()
            user.save()

            return render(request, 'register_done.html', {'user': user})

    return render(request, 'register.html', {'user_form': user_form})


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        profile = Profile.objects.get(user=user)
        # print(profile)
        if user is not None:

            access_token = create_jwt(user.id, user.username, token_type='access')
            refresh_token = create_jwt(user.id, user.username, token_type='refresh')

            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token

            django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # print(request.user.is_authenticated)

            response = redirect('profile')
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
            return response
        else:
            messages.error(request, 'Something went wrong')

    return render(request, 'login.html', {'form': form})

def google_login(request):
    user = request.user

    google_profile_data = request.session.get('google_profile_data', {})
    photo = google_profile_data.get('picture')

    user_obj = User.objects.get(username=user)

    try:
        profile = Profile.objects.get(user=user)
        print(photo)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        profile.email_confirmed = True
        profile.photo = photo
        profile.save()

    access_token = create_jwt(user.id, user.username, token_type='access')
    refresh_token = create_jwt(user.id, user.username, token_type='refresh')

    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    response = redirect('profile')
    response.set_cookie('access_token', access_token, httponly=True)
    response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
    return response

