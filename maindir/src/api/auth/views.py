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

from api.auth.forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm


def logout_user(request):
    # logout(request)
    # response = redirect('logogu')
    # response.delete_cookie('access_token')
    # response.delete_cookie('refresh_token')
    return render(request, 'logout.html')
    # return JsonResponse({'message': 'User logged out successfully'})

def force_logout(user):

    user.refresh_token.delete()
    logout(user)
    return JsonResponse({'message': 'User logged out due to expired token'}, status=401)

def register(request):
    user_form = UserRegistrationForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse('register.html', context={'error': 'Username already taken'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return render(request, 'register_done.html', {'new_user': user})
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


            django_login(request, user)

            response = redirect('profile')
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
            return response
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

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
    #
    # if not user.get('is_authenticated', False):
    #     return JsonResponse({'error': 'User is not authenticated'}, status=401)

    return render(request, 'profile.html', {
        'username': user['user_name'],
        # 'email': user['email'],
    })