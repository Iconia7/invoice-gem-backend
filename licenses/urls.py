from django.urls import path
from .views import VerifyPaymentView, CheckLicenseStatusView, InitializePaymentView

urlpatterns = [
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('status/', CheckLicenseStatusView.as_view(), name='check-license'),
    path('initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
]
