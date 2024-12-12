from django.contrib.auth.models import User
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from utils.decoraters import token_required, email_verified_required
from apps.profile.models import Profile

from apps.auth_user.forms import ProfileEditForm

from apps.auth_user.forms import UserEditForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import EmailVerifyForm


@email_verified_required
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
    print(user_obj)
    profile_obj = Profile.objects.get(user=user_obj)

    return render(request, 'profile.html', {
        'user_obj': user_obj,
        'profile_obj': profile_obj,
        'photo': profile_obj.photo.url if profile_obj.photo else None,
    })

@token_required
def profile_email_for_verify(request):
    if request.method == 'POST':
        form = EmailVerifyForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Something went wrong')
            user_payload = request.user
            username = user_payload.get('user_name')
            user = User.objects.get(username=username)

            current_site = get_current_site(request)
            activation_url = reverse('activate', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'email': email
            })

            mail_subject = 'Activate your account'
            print(activation_url)
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'activation_url': activation_url,
            })
            to_email = email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.content_subtype = "html"
            email.send()

            return redirect('verify_done')
    else:
        form = EmailVerifyForm()

    return render(request, 'profile_email_for_verify.html', {'form': form})


def activate(request, uidb64, token, email):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        profile = Profile.objects.get(user=user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email = email
        user.save()

        profile.email_confirmed = True
        profile.save()

        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('profile')
    else:
        return render(request, 'email_confirmation_invalid.html')


def verify_done(request):
    return render(request, 'verify_done.html')