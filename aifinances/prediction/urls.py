from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('predict/', views.PredictionAPI.as_view(), name='predict'),
]