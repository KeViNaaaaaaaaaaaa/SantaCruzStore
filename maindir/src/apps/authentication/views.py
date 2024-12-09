from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from utils.helpers import create_jwt, decode_jwt
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib import messages

from apps.authentication.forms import LoginForm, UserRegistrationForm

from apps.profile.models import Profile



def logout_user(request):
    logout(request)  # Деаутентифицируем пользователя
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
            # email = user_form.cleaned_data['email']
            if User.objects.filter(username=username).exists():
                return render(request, 'register.html', {'user_form': user_form, 'error': 'Username already taken'})
            # if User.objects.filter(email=email).exists():
            #     return render(request, 'register.html', {'user_form': user_form, 'error': 'Email already taken'})

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
        if user is not None:

            access_token = create_jwt(user.id, user.username, token_type='access')
            refresh_token = create_jwt(user.id, user.username, token_type='refresh')

            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token

            django_login(request, user)
            # print(request.user.is_authenticated)

            response = redirect('profile')
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
            return response
        else:
            messages.error(request, 'Something went wrong')

    return render(request, 'login.html', {'form': form})





