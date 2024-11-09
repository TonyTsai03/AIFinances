from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import StockPredictor

class PredictionAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.predictor = StockPredictor()

    def post(self, request):
        try:
            company_code = request.data.get('company_code')
            if not company_code:
                return Response({
                    'status': 'error',
                    'message': '請提供股票代碼'
                }, status=status.HTTP_400_BAD_REQUEST)

            predictions = self.predictor.predict(company_code)
            
            if predictions is None:
                return Response({
                    'status': 'error',
                    'message': '預測過程發生錯誤'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'status': 'success',
                'company_code': company_code,
                'predictions': predictions
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)