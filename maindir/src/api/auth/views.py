import datetime

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from utils.decoraters import token_required
import json
from utils.helpers import create_jwt, decode_jwt
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib import messages

from api.auth.forms import LoginForm, UserRegistrationForm, RegistrationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

from apps.authentication.models import Profile

from api.auth.forms import ProfileEditForm

from api.auth.forms import UserEditForm

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from config import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required


def logout_user(request):
    logout(request)  # Деаутентифицируем пользователя
    response = render(request, 'logout.html', {'message': 'Logged out successfully'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@login_required
@token_required
def my_protected_view(request):
    # Получаем текущего пользователя
    user = request.user

    # Если пользователь аутентифицирован, возвращаем его данные
    if user.is_authenticated:
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)


def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html"  # Убедитесь, что содержимое письма в формате HTML
    email.send()


def register(request):
    user_form = UserRegistrationForm()
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']
            if User.objects.filter(username=username).exists():
                return render(request, 'register.html', {'user_form': user_form, 'error': 'Username already taken'})
            if User.objects.filter(email=email).exists():
                return render(request, 'register.html', {'user_form': user_form, 'error': 'Email already taken'})

            user = User.objects.create_user(username=username, password=password, email=email)
            user.is_active = False
            user.save()

            send_activation_email(request, user)
            return render(request, 'register_done.html', {'user': user})

    return render(request, 'register.html', {'user_form': user_form})


def activate(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
    else:
        return render(request, 'email_confirmation_invalid.html')


@token_required
def profile_edit(request):
    user = request.user
    try:
        user_obj = User.objects.get(id=user['user_id'])
        profile_obj = Profile.objects.get(user=user_obj)
    except (User.DoesNotExist, Profile.DoesNotExist):
        return JsonResponse({'error': 'User or profile not found'}, status=404)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_obj)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile_obj)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=user_obj)
        profile_form = ProfileEditForm(instance=profile_obj)

    return render(request, 'profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:

            access_token = create_jwt(user.id, user.username, token_type='access')
            refresh_token = create_jwt(user.id, user.username, token_type='refresh')

            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token

            django_login(request, user)
            print(request.user.is_authenticated)

            response = redirect('profile')
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
            return response
        else:
            messages.error(request, 'Something went wrong')

    return render(request, 'login.html', {'form': form})


@token_required
def profile(request):
    if request.method == 'POST':
        response = redirect('logout')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

    user = request.user
    print(user)
    user_obj = User.objects.get(username=user['user_name'])
    django_login(request, user_obj, backend='django.contrib.auth.backends.ModelBackend')
    profile_obj = Profile.objects.get(user=user_obj)

    return render(request, 'profile.html', {
        'username': user_obj.username,
        'email': user_obj.email,
        'first_name': user_obj.first_name,
        'last_name': user_obj.last_name,
        'date_of_birth': profile_obj.date_of_birth,
        'photo': profile_obj.photo.url if profile_obj.photo else None,
    })
