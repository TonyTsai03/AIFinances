from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('random-stocks/', views.RandomStocksAPI.as_view(), name='random_stocks'),
    path('favorites/', views.ListFavoriteStocksAPI.as_view(), name='list_favorites'),
    path('favorites/add/', views.FavoriteStockAPI.as_view(), name='add_favorite'),
    path('favorites/<str:stock_id>/remove/', views.FavoriteStockAPI.as_view(), name='remove_favorite'),
    path('search/', views.SearchStocksAPI.as_view(), name='search_stocks'),
]