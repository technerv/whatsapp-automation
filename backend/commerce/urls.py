from django.urls import path
from .views import InitiatePaymentView, MpesaCallbackView, ProductListView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('mpesa-callback/', csrf_exempt(MpesaCallbackView.as_view()), name='mpesa-callback'),
]