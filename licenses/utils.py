import jwt
import datetime
from django.conf import settings

def generate_pro_token(device_id):
    """
    Generates a signed JWT for a given device_id.
    """
    payload = {
        'device_id': device_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365 * 10), # Valid for 10 years
        'scope': 'pro_features'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_pro_token(token):
    """
    Verifies a JWT and returns the payload if valid.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
