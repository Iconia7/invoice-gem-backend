import africastalking
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .models import EmailOTP
from django.conf import settings

# Initialize Africa's Talking
africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms_service = africastalking.SMS

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        method = request.data.get('method', 'sms') # 'sms' or 'email'

        if not email and not phone:
            return Response({'error': 'Email or phone is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and save OTP
        otp_obj = EmailOTP.generate_otp(email=email, phone=phone)

        if method == 'sms' and phone:
            # Send SMS via Africa's Talking
            message = f'Your Invoice Gem verification code is: {otp_obj.code}. Expires in 10 mins.'
            sender = settings.AFRICASTALKING_SENDER_ID or None
            
            try:
                # Africa's Talking expects recipients as a list
                response = sms_service.send(message, [phone], sender_id=sender)
                return Response({
                    'status': 'success', 
                    'message': 'OTP sent via SMS',
                    'af_response': response
                }, status=status.HTTP_200_OK)
            except Exception as e:
                # Fallback to email if SMS fails and email is provided
                if email:
                    return self._send_email_otp(email, otp_obj.code)
                return Response({'error': f'SMS failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif email:
            # Send Email
            return self._send_email_otp(email, otp_obj.code)
        
        else:
            return Response({'error': 'Invalid request parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def _send_email_otp(self, email, code):
        subject = 'Your Invoice Gem Verification Code'
        message = f'Your verification code is: {code}\n\nThis code will expire in 10 minutes.'
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
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        if (not email and not phone) or not code:
            return Response({'error': 'Email/Phone and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the latest unexpired OTP for this identity
        if email:
            otp_obj = EmailOTP.objects.filter(email=email, code=code, is_verified=False).last()
        else:
            otp_obj = EmailOTP.objects.filter(phone=phone, code=code, is_verified=False).last()

        if not otp_obj:
            return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            return Response({'error': 'Verification code has expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as verified
        otp_obj.is_verified = True
        otp_obj.save()

        return Response({'status': 'success', 'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
