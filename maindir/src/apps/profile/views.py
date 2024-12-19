from idlelib.autocomplete import TRY_A

from django.contrib.auth.models import User
from django.contrib import messages
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from utils.decoraters import token_required, email_verified_required
from apps.profile.models import Profile, Promocode

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import EmailVerifyForm, UserEditForm, ProfileEditForm
from apps.orders.models import Order, OrderItem, Cart
from apps.catalog.models import Like
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
import string


def photo_form(request):
    user = request.user
    photo_prof = False
    if isinstance(user, dict):
        profile_obj = Profile.objects.get(user=user['user_id'])
        photo_prof = True
    else:
        try:
            profile_obj = Profile.objects.get(user=user)
            print(profile_obj)
            photo_prof = True
        except:
            pass
        print(photo_prof)
    return {'photo': profile_obj.photo.url if photo_prof else None}


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
    user_obj = User.objects.get(username=user['user_name'])
    orders = Order.objects.filter(user=user_obj)
    django_login(request, user_obj, backend='django.contrib.auth.backends.ModelBackend')
    profile_obj = Profile.objects.get(user=user_obj)

    return render(request, 'profile.html', {
        'user_obj': user_obj,
        'profile_obj': profile_obj,
        'orders': orders,
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

            try:
                acc_with_promo = Promocode.objects.get(email=email)
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

            except:

                message = render_to_string('acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'activation_url': activation_url,
                    'gift': default_token_generator.make_token(user)[:8],
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
        try:
            Promocode.objects.get(email=email)
        except:
            Promocode.objects.create(promocode=token[:8], email=email)
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


@email_verified_required
@token_required
def order_detail(request, order_id):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    order = get_object_or_404(Order, id=order_id, user=user_obj)
    return render(request, 'order_detail.html', {'order': order})


@email_verified_required
@token_required
def order_delete(request, order_id):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    order = get_object_or_404(Order, id=order_id, user=user_obj)
    order.delete()
    return redirect('profile')


@token_required
def profile_delete(request):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    profile = Profile.objects.get(user=user_obj)
    email_confirmed = profile.email_confirmed

    if email_confirmed:
        open_orders = Order.objects.filter(user=user_obj, status='open')
        if open_orders.exists():
            messages.error(request, 'You cannot delete your account because you have open orders.')
            return redirect('profile')
        try:
            EmailAddress.objects.get(user=user_obj).delete()
            SocialAccount.objects.get(user=user_obj).delete()
        except:
            pass


        Order.objects.filter(user=user_obj).delete()
        for i in Order.objects.filter(user=user_obj):
            OrderItem.objects.filter(order=i).delete()
        Cart.objects.filter(user=user_obj).delete()

    Like.objects.filter(user=user_obj).delete()
    Profile.objects.filter(user=user_obj).delete()

    user_obj.delete()

    response = render(request, 'home.html', {'message': 'Logged out successfully'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
