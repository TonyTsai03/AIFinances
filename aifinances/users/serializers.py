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

        if not email or not password:
            raise serializers.ValidationError("必須提供電子郵件和密碼")
            
        try:
            # 首先通過郵箱查找用戶
            user = User.objects.get(email=email)
            
            # 檢查密碼
            if user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError("用戶帳號已被禁用")
                # 設置驗證通過的用戶
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("密碼不正確")
                
        except User.DoesNotExist:
            raise serializers.ValidationError("此電子郵件未註冊")

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
            raise serializers.ValidationError('電子郵件不存在')
        
        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email = email)
        user.set_password(new_password)
        user.save()

        return user
    
class UpdateProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('用戶名稱重複')
        return value

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('此電子郵件已被註冊')
        return value

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data['username']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        instance.save()
        return instance

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密碼不正確')
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance