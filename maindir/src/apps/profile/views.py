from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from utils.decoraters import token_required
from apps.profile.models import Profile

from apps.authentication.forms import ProfileEditForm

from apps.authentication.forms import UserEditForm



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