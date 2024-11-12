from rest_framework import serializers
from .models import FavoriteStock

class FavoriteStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteStock
        fields = ('id', 'stock_id', 'stock_name', 'created_at')
        read_only_fields = ('created_at',)