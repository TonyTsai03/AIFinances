from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path('login/', views.LoginAPI.as_view(), name='login'),
    path('forget-password/', views.ForgetPasswordAPI.as_view(), name='forget_password'),
    path('verify-otp/', views.VerifyOTPAPI.as_view(), name='verify_otp'),
    path('reset-profile/', views.ResetUserNameAndPasswordAPI.as_view(), name='reset-profile'),
]