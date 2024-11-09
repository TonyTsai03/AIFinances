from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import get_random_stocks, FavoriteStock, search_stocks
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from .serializers import FavoriteStockSerializer


class RandomStocksAPI(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            try:
                count = int(request.query_params.get('count',5))
                count = max(1, min(20, count))
            
            except ValueError:
                return Response({
                    'status': 'error',
                    'message': 'value error'
                }, status = status.HTTP_400_BAD_REQUEST)
            
            random_stocks = get_random_stocks()
            if random_stocks is None:
                return Response({
                    'status':'error',
                    'message': '無法獲取資料'
                }, status = status.HTTP_503_SERVICE_UNAVAILABLE)
            
            if not random_stocks:
                return Response({
                'status': 'error',
                'data': '沒有可用的股票資料'
            }, status = status.HTTP_503_SERVICE_UNAVAILABLE)
        
            return Response({
                'status': 'success',
                'data': random_stocks
            }, status = status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FavoriteStockAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_id = request.data.get('stock_id')
        stock_name = request.data.get('stock_name')

        if not stock_id or not stock_name:
            return Response({
                'status':'error',
                'message':'沒有收到股票代碼或是名稱'
            }, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = FavoriteStock.objects.create(
                user = request.user,
                stock_id = stock_id,
                stock_name = stock_name
            )
            return Response({
                'status':'success',
                'message':'成功加入收藏',
                'date': FavoriteStockSerializer(favorite).data
            }, status = status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'status':'error',
                'message': '已經存在收藏中'
            }, status = status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, stock_id):
        try:
            favorite = FavoriteStock.objects.get(
                user = request.user,
                stock_id = stock_id
            )

            favorite.delete()
            return Response({
                'status': 'success',
                'message': '成功取消收藏'
            })
        except FavoriteStock.DoesNotExist:
            return Response({
                'status':'error',
                'message':'該股票不在收藏內'
            }, status = status.HTTP_400_BAD_REQUEST)


class ListFavoriteStocksAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteStockSerializer

    def get_queryset(self):
        return FavoriteStock.objects.filter(user=self.request.user)
    
class SearchStocksAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()

            if not query:
                return Response({
                    'status':'error',
                    'message':'請輸入關鍵字'
                }, status = status.HTTP_400_BAD_REQUEST)
            
            if len(query) < 2:
                return Response({
                    'status':'error',
                    'message':'至少兩個字'
                }, status = status.HTTP_400_BAD_REQUEST)
            
            resutls = search_stocks(query)

            if resutls is None:
                return Response({
                    'status':'error',
                    'message':'搜尋過程發生錯誤'
                }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'status':'success',
                'count': len(resutls),
                'data': resutls
            }, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status':'error',
                'message': str(e)
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)