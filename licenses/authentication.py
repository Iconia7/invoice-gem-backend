from rest_framework import authentication, exceptions
from .utils import verify_pro_token
from .models import ProLicense

class ProLicenseUser:
    """Mock user object to satisfy DRF's authentication system"""
    def __init__(self, pro_license):
        self.pro_license = pro_license
        self.is_authenticated = True

    @property
    def pk(self):
        return self.pro_license.pk

class ProJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None

        payload = verify_pro_token(token)
        if not payload:
            raise exceptions.AuthenticationFailed('Invalid or expired token')

        device_id = payload.get('device_id')
        try:
            pro_license = ProLicense.objects.get(device_id=device_id, is_active=True)
            return (ProLicenseUser(pro_license), token)
        except ProLicense.DoesNotExist:
            raise exceptions.AuthenticationFailed('No active license found for this device')
