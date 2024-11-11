import finlab
from finlab import data
import random
from django.core.cache import cache
from django.db import models
from django.contrib.auth import get_user_model
import pandas as pd
User = get_user_model()

def get_random_stocks():
    cache_data = cache.get('company_data')

    if cache_data is None:
        finlab.login('r0K9y4lF4EhgdSIjBVE5vY7ZKMhXqNr/N0yWFGz/keCB1a87U4N1xykyUlLu9B7S#vip_m')
        company_data = data.get('company_basic_info')
        cache.set('company_data', company_data, 86400)
    else:
        company_data = cache_data

    stocks_info = company_data[['stock_id', '公司簡稱']].copy()
    random_stocks = stocks_info.sample(n=5)
    result = random_stocks.to_dict('records')
    
    return result

class FavoriteStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'favorite_stock')
    stock_id = models.CharField(max_length = 10)
    stock_name = models.CharField(max_length = 50)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('user', 'stock_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.stock_id} ({self.stock_name})"

def search_stocks(query):
    try:
        cached_data = cache.get('company_data')
        CACHE_TIMEOUT = 86400

        if cached_data is None:
            finlab.login('r0K9y4lF4EhgdSIjBVE5vY7ZKMhXqNr/N0yWFGz/keCB1a87U4N1xykyUlLu9B7S#vip_m')
            company_data = data.get('company_basic_info')
            stocks_info = company_data[['stock_id', '公司簡稱']].copy()
            cache.set('company_data', stocks_info, CACHE_TIMEOUT)
        else:
            stocks_info = cached_data
        
        mask = (stocks_info['stock_id'].str.contains(query, case = False, na = False) |
                stocks_info['公司簡稱'].str.contains(query, case = False, na = False))
        
        matched_stocks = stocks_info[mask].head(20)
        return matched_stocks.to_dict('records')
    
    except Exception as e:
        print(e)
        return None
    
