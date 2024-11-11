from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ForgetPassword, OTPVerificationSerializer, ResetPasswordSerializer, ResetUserNameAndPassword
import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token.key
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordAPI(generics.GenericAPIView):
    serializer_class = ForgetPassword
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = ''.join([str(random.randint(0,9)) for _ in range(4)])
            cache.set(f'otp_{email}', otp, timeout=300)
            send_mail(
                'Password Reset OTP',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPI(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({"message":"OTP verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      

class ResetPasswordAPI(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetUserNameAndPasswordAPI(generics.GenericAPIView):
   serializer_class = ResetUserNameAndPassword
   
   permission_classes = [IsAuthenticated]

   def post(self, request):
       serializer = self.get_serializer(
           instance = request.user,
           data = request.data,
           context = {'request': request}
       )

       if serializer.is_valid(): 
           user = serializer.update(request.user, serializer.validated_data)

           Token.objects.filter(user=user).delete()
           new_token = Token.objects.create(user=user)

           return Response({
               'message':'更新成功',
               'user': UserSerializer(user).data,
               'newToken': new_token.key
           }, status = status.HTTP_200_OK)
       
       return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)