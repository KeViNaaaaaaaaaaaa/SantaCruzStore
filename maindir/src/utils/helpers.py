import jwt
import datetime
from django.conf import settings


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
