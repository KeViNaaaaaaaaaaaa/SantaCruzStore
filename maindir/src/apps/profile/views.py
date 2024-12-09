from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from utils.decoraters import token_required
from apps.profile.models import Profile

from apps.authentication.forms import ProfileEditForm

from apps.authentication.forms import UserEditForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required


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

@token_required
def send_activation_email(request):
    user_payload = request.user
    username = user_payload.get('user_name')
    user = User.objects.get(username=username)
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
    email.content_subtype = "html"
    email.send()
    return render(request, 'register_done.html', {'user': user})

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
        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('profile')
    else:
        return render(request, 'email_confirmation_invalid.html')