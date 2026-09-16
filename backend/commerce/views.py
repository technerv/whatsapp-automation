from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, Order
from .services import initiate_stk_push
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class InitiatePaymentView(APIView):
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        phone_number = request.data.get('phone_number')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(product=product, customer_phone=phone_number)

        mpesa_response = initiate_stk_push(phone_number, int(product.price), order.id)

        if mpesa_response and mpesa_response.get('CheckoutRequestID'):
            order.checkout_request_id = mpesa_response['CheckoutRequestID']
            order.save()
            return Response(mpesa_response, status=status.HTTP_200_OK)
        else:
            order.status = 'failed'
            order.save()
            return Response({"error": "Failed to initiate M-PESA payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MpesaCallbackView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        
        try:
            order = Order.objects.get(checkout_request_id=checkout_request_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        if result_code == 0:
            order.status = 'paid'
            order.save()
        else:
            order.status = 'failed'
            order.save()
            
        return Response(status=status.HTTP_200_OK)