from django.db import models
import random
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        # OTP expires in 10 minutes
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @classmethod
    def generate_otp(cls, email=None, phone=None):
        code = str(random.randint(100000, 999999))
        return cls.objects.create(email=email, phone=phone, code=code)

    def __str__(self):
        return f"OTP for {self.email or self.phone} - {self.code}"
