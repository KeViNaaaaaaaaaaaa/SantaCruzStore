import random
import string

from django.contrib.auth.models import User

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from utils.helpers import create_jwt, decode_jwt
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.auth_user.forms import LoginForm, UserRegistrationForm

from apps.profile.models import Profile

from utils.decoraters import token_required

from apps.profile.models import Promocode
from apps.catalog.models import Like


# @token_required
# def photo_form(request):
#     user = request.user
#     user_true = False
#     try:
#         u = []
#         user_obj = User.objects.get(id=user['user_id'])
#         is_liked = Like.objects.filter(user=user_obj)
#         for i in is_liked:
#             u.append(i.product)
#         user_true = True
#     except:
#         pass
#
#     return {'user': user_obj if user_true else None}


def logout_user(request):
    logout(request)
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
            profile = Profile.objects.create(user=user,
                                             photo='/users/2024/12/12/santa-cruz-bronson-cc-x0-axs-rsv-2024-491972-1_Rqlx7yL.png')
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
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            if user.is_superuser:
                profile = Profile.objects.create(user=user,
                                                 photo='/users/2024/12/12/santa-cruz-bronson-cc-x0-axs-rsv-2024-491972-1_Rqlx7yL.png')
                profile.email_confirmed = True
                profile.save()
            return JsonResponse({'error': 'User or profile not found'}, status=404)
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

    # user_obj = User.objects.get(username=user)

    photo = '/users/2024/12/12/santa-cruz-bronson-cc-x0-axs-rsv-2024-491972-1_Rqlx7yL.png'

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        profile.email_confirmed = True
        profile.photo = photo
        profile.save()

    try:
        Promocode.objects.get(email=user.email)
    except:
        characters = string.ascii_letters + string.digits
        promo_code = ''.join(random.choice(characters) for i in range(8))
        Promocode.objects.create(promocode=promo_code, email=user.email)
        message = render_to_string('promocode_for_google_auth.html', {
            'user': user,
            'promo_code': promo_code,
        })
        to_email = user.email
        print(to_email, 'sdas')
        mail_subject = 'Promocode for your account'
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = "html"
        email.send()

    access_token = create_jwt(user.id, user.username, token_type='access')
    refresh_token = create_jwt(user.id, user.username, token_type='refresh')

    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token

    response = redirect('profile')
    response.set_cookie('access_token', access_token, httponly=True)
    response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
    return response
