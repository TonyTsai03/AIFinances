from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("此電子郵件已被註冊")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=email)
                    if not user_obj.check_password(password):
                        raise serializers.ValidationError("密碼不正確")
                except User.DoesNotExist:
                    raise serializers.ValidationError("此電子郵件未註冊")
            if user and not user.is_active:
                raise serializers.ValidationError("用戶帳號已被禁用")
        else:
            raise serializers.ValidationError("必須提供電子郵件和密碼")

        data['user'] = user
        return data

class ForgetPassword(serializers.Serializer):
    email = serializers.EmailField()

    def validateEmail(self, value):
        if not User.objects.filter(email = value).exists():
            raise serializers.ValidationError("此電子郵件未註冊")
        return value

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length = 4, min_length = 4)

    def validate(self, data):

        email = data.get('email')
        otp = data.get('otp')
        stored_otp = cache.get(f"otp_{email}")

        if not stored_otp or stored_otp != otp:
            raise serializers.ValidationError('OTP無效')
        
        return data
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only = True)
    
    def validate(self, data):
        email = data.get('email')

        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            raise serializers.ValidationError('用戶不存在')
        
        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email = email)
        user.set_password(new_password)
        user.save()

        return user
    
class ResetUserNameAndPassword(serializers.Serializer):
    username = serializers.CharField(required = True)
    new_password = serializers.CharField(write_only = True, requird = True)

    def validate_username(self, value):
        user = self.context['request'].user

        if User.objects.filter(username = value).exclude( id = user.id).exists():
            raise serializers.ValidationError('用戶名稱重複')
        
        return value
    
    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.set_password  = validated_data['new_password']
        instance.save()
        return instance
