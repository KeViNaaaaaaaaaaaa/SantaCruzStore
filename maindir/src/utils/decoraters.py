from datetime import datetime
from functools import wraps

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from utils.helpers import decode_jwt, create_jwt
import jwt
from django.contrib.auth import logout
# from apps.auth_user.models import RefreshToken

from config import settings

from apps.profile.models import Profile


# from apps.authentication.views import refresh_token


# def token_required(f):
#     @wraps(f)
#     def decorated_function(request, *args, **kwargs):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header:
#             return JsonResponse({'error': 'Authorization header required'}, status=401)
#
#         token = auth_header.split(' ')[1]
#         payload = decode_jwt(token)
#         if not payload:
#             return JsonResponse({'error': 'Invalid or expired token'}, status=401)
#
#         # Проверка срока действия access токена
#         if payload['exp'] < datetime.datetime.utcnow().timestamp():
#             # Попытка обновить access токен с использованием refresh токена
#             try:
#                 refresh_token = RefreshToken.objects.get(user_id=payload['user_id']).token
#                 refresh_payload = decode_jwt(refresh_token)
#                 if refresh_payload['exp'] < datetime.datetime.utcnow().timestamp():
#                     return force_logout(request.user)
#
#                 # Генерация нового access токена
#                 new_access_token = create_jwt(payload['user_id'], token_type='access')
#                 request.session['access_token'] = new_access_token
#                 return f(request, *args, **kwargs)
#
#             except RefreshToken.DoesNotExist:
#                 return JsonResponse({'error': 'Refresh token not found'}, status=401)
#             except jwt.ExpiredSignatureError:
#                 return JsonResponse({'error': 'Refresh token expired'}, status=401)
#             except jwt.InvalidTokenError:
#                 return JsonResponse({'error': 'Invalid refresh token'}, status=400)
#
#         return f(request, *args, **kwargs)
#
#     return decorated_function
def token_required(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        if not token:
            return JsonResponse({'error': 'Token is missing'}, status=401)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            refresh_token_value = request.COOKIES.get('refresh_token')
            if not refresh_token_value:
                return JsonResponse({'error': 'Refresh token is missing'}, status=401)

            try:
                refresh_payload = decode_jwt(refresh_token_value)
                if refresh_payload != None:
                    print(refresh_payload)
                    if refresh_payload['type'] != 'refresh':
                        return JsonResponse({'error': 'Invalid token type'}, status=400)

                    user = User.objects.get(id=refresh_payload['user_id'])

                    access_token = create_jwt(user.id, user.username, token_type='access')

                    response = redirect('profile')
                    response.set_cookie('access_token', access_token, httponly=True)
                    return response
                else:
                    logout(request)
                    return HttpResponseRedirect("/api/auth/login")
                    # return render(request, 'login.html')
                    # return JsonResponse({'error': 'Invalid token type'}, status=400)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Refresh token expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=400)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        request.user = payload
        return f(request, *args, **kwargs)

    return decorated


def email_verified_required(f):
    """
    Декоратор, который проверяет, подтверждён ли email пользователя.
    Если email не подтверждён, возвращает ошибку 403 (Forbidden).
    """
    @wraps(f)
    def decorated(request, *args, **kwargs):
        user_payload = request.user
        if not user_payload:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        try:
            # Получаем пользователя и профиль
            user = User.objects.get(username=user_payload)
            profile = Profile.objects.get(user=user)
        except (User.DoesNotExist, Profile.DoesNotExist):
            return JsonResponse({'error': 'User or profile not found'}, status=404)

        if not profile.email_confirmed:
            return JsonResponse({'error': 'Email not verified'}, status=403)

        return f(request, *args, **kwargs)

    return decorated