import jwt
import datetime
from config import settings


def get_client_ip(request):
    """
    Get user's IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    return ip


def create_jwt(user_id, user_name, token_type='access'):
    expires = (
        settings.JWT_ACCESS_TOKEN_EXPIRES
        if token_type == 'access'
        else settings.JWT_REFRESH_TOKEN_EXPIRES
    )
    payload = {
        'user_id': user_id,
        'user_name': user_name,
        'type': token_type,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires),
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
