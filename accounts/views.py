from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .models import EmailOTP
from django.conf import settings

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and save OTP
        otp_obj = EmailOTP.generate_otp(email)

        # Send Email
        subject = 'Your Invoice Gem Verification Code'
        message = f'Your verification code is: {otp_obj.code}\n\nThis code will expire in 10 minutes.'
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
            return Response({'status': 'success', 'message': 'OTP sent to your email'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the latest unexpired OTP for this email
        otp_obj = EmailOTP.objects.filter(email=email, code=code, is_verified=False).last()

        if not otp_obj:
            return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            return Response({'error': 'Verification code has expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as verified
        otp_obj.is_verified = True
        otp_obj.save()

        return Response({'status': 'success', 'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
