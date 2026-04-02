import requests
import africastalking
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import ProLicense
from .utils import generate_pro_token

# Initialize Africa's Talking
africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms_service = africastalking.SMS

class VerifyPaymentView(APIView):
    permission_classes = [] # Allow unauthenticated POST for verification

    def post(self, request):
        device_id = request.data.get('device_id')
        reference = request.data.get('reference')
        phone = request.data.get('phone')

        if not device_id or not reference:
            return Response({'error': 'device_id and reference are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if reference already used
        if ProLicense.objects.filter(paystack_reference=reference).exists():
            return Response({'error': 'This payment reference has already been used'}, status=status.HTTP_400_BAD_REQUEST)

        # Call Paystack to verify
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if not data.get('status') or data['data']['status'] != 'success':
                return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify amount based on currency
            amount_paid = data['data']['amount']
            currency = data['data']['currency']
            
            is_valid_amount = False
            if currency == 'KES' and amount_paid >= settings.PRO_PRICE_KSH_CENTS:
                is_valid_amount = True
            elif currency == 'USD' and amount_paid >= settings.PRO_PRICE_USD_CENTS:
                is_valid_amount = True
            elif currency == 'NGN' and amount_paid >= settings.PRO_PRICE_KSH_CENTS: # Fallback if Kobo was used
                is_valid_amount = True

            if not is_valid_amount:
                return Response({'error': f'Insufficient payment amount for {currency}'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Issue License
            token = generate_pro_token(device_id)
            license, created = ProLicense.objects.update_or_create(
                device_id=device_id,
                defaults={
                    'paystack_reference': reference,
                    'jwt_token': token,
                    'is_active': True,
                    'amount_paid': amount_paid,
                }
            )

            # Send Congratulatory SMS if phone is provided
            if phone:
                try:
                    message = "Congratulations! Your Invoice Gem Pro Lifetime access has been activated successfully. Thank you for choosing Invoice Gem!"
                    sender = settings.AFRICASTALKING_SENDER_ID or None
                    sms_service.send(message, [phone], sender_id=sender)
                except Exception as sms_err:
                    # Don't fail the verification if SMS fails
                    print(f"SMS Error: {sms_err}")
            
            return Response({
                'status': 'success',
                'token': token,
                'is_pro': True
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckLicenseStatusView(APIView):
    def get(self, request):
        # The user's device_id is in the JWT payload if we used JWT auth
        # For simplicity, we'll just check if the token in the header is valid
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'is_pro': False}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        from .utils import verify_pro_token
        payload = verify_pro_token(token)
        
        if not payload:
            return Response({'is_pro': False}, status=status.HTTP_401_UNAUTHORIZED)
        
        device_id = payload.get('device_id')
        try:
            license = ProLicense.objects.get(device_id=device_id, is_active=True)
            return Response({'is_pro': True, 'device_id': device_id}, status=status.HTTP_200_OK)
        except ProLicense.DoesNotExist:
            return Response({'is_pro': False}, status=status.HTTP_401_UNAUTHORIZED)

class InitializePaymentView(APIView):
    permission_classes = [] 

    def post(self, request):
        email = request.data.get('email')
        amount = request.data.get('amount') # in cents/kobo
        currency = request.data.get('currency', 'KES')

        if not email or not amount:
            return Response({'error': 'email and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "amount": amount,
            "currency": currency,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()
            if data.get('status'):
                return Response(data['data'], status=status.HTTP_200_OK)
            else:
                return Response({'error': data.get('message')}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
