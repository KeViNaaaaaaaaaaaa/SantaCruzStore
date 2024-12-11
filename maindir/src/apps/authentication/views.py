from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from utils.helpers import create_jwt, decode_jwt
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib import messages

from apps.authentication.forms import LoginForm, UserRegistrationForm

from apps.profile.models import Profile

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
            email = user_form.cleaned_data['email']
            if User.objects.filter(username=username).exists():
                return render(request, 'register.html', {'user_form': user_form, 'error': 'Username already taken'})
            if User.objects.filter(email=email).exists():
                return render(request, 'register.html', {'user_form': user_form, 'error': 'Email already taken'})

            user = User.objects.create_user(username=username, password=password, email=email)
            profile = Profile.objects.create(user=user)
            profile.save()
            user.save()

            send_activation_email(request, user)

            return render(request, 'register_done.html', {'user': user})

    return render(request, 'register.html', {'user_form': user_form})


def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
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


def activate(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        profile = Profile.objects.get(user=user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        profile.email_confirmed = True
        profile.save()
        user.save()
        return redirect('home')
    else:
        return render(request, 'email_confirmation_invalid.html')
