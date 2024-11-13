from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path('login/', views.LoginAPI.as_view(), name='login'),
    path('ResetPassword/', views.ResetPasswordAPI.as_view(), name='reset_password'),
    path('forget-password/', views.ForgetPasswordAPI.as_view(), name='forget_password'),
    path('verify-otp/', views.VerifyOTPAPI.as_view(), name='verify_otp'),
    path('update-profile/', views.UpdateProfileAPI.as_view(), name='update-profile'),
    path('update-password/', views.UpdatePasswordAPI.as_view(), name='update-password'),
]