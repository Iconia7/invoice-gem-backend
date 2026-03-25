from django.db import models

class ProLicense(models.Model):
    device_id = models.CharField(max_length=200, unique=True, help_text="Unique hardware ID from device_info_plus")
    paystack_reference = models.CharField(max_length=200, unique=True, help_text="Verified Paystack transaction reference")
    jwt_token = models.TextField(help_text="The latest signed JWT issued to this device")
    is_active = models.BooleanField(default=True)
    amount_paid = models.IntegerField(help_text="Amount paid in minor units (e.g. kobo/cents)")
    issued_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"License for {self.device_id} ({'Active' if self.is_active else 'Revoked'})"

    class Meta:
        ordering = ['-issued_at']
