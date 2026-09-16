from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import Order, OrderItem, Invoice, Receipt
from .serializers import OrderSerializer, OrderItemSerializer, InvoiceSerializer, ReceiptSerializer
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(business=self.request.user.business).prefetch_related('items')

    def perform_create(self, serializer):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        serializer.save()

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            raise ValidationError({'status': 'This field is required.'})
        try:
            order.transition_to(new_status)
        except ValueError as exc:
            raise ValidationError({'status': str(exc)}) from exc
        order.save(update_fields=['status'])
        return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__business=self.request.user.business)

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(order__business=self.request.user.business)

class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Receipt.objects.filter(invoice__order__business=self.request.user.business)