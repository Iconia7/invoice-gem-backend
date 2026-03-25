from django.urls import path
from .views import VerifyPaymentView, CheckLicenseStatusView

urlpatterns = [
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('status/', CheckLicenseStatusStatusView.as_view() if False else CheckLicenseStatusView.as_view(), name='check-license'),
]

# Note: The typo in function name above was caught and fixed in the actual code below:
from django.urls import path
from .views import VerifyPaymentView, CheckLicenseStatusView

urlpatterns = [
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('status/', CheckLicenseStatusView.as_view(), name='check-license'),
]
