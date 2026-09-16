from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import Cart, CartItem, Order, OrderItem, Invoice, Receipt
from .serializers import CartItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, InvoiceSerializer, ReceiptSerializer
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


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(business=self.request.user.business).prefetch_related('items__product')

    def perform_create(self, serializer):
        if not self.request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        serializer.save(business=self.request.user.business)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        cart = self.get_object()
        if cart.status != 'active':
            raise ValidationError({'detail': 'Only active carts can be changed.'})
        item_serializer = CartItemSerializer(data=request.data, context={'request': request})
        item_serializer.is_valid(raise_exception=True)
        item, _ = CartItem.objects.update_or_create(
            cart=cart,
            product=item_serializer.validated_data['product'],
            defaults={'quantity': item_serializer.validated_data['quantity']},
        )
        return Response(CartItemSerializer(item, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
        if cart.status != 'active':
            raise ValidationError({'detail': 'Only active carts can be checked out.'})
        items = list(cart.items.select_related('product'))
        if not items:
            raise ValidationError({'detail': 'Cannot check out an empty cart.'})
        order_serializer = OrderSerializer(
            data={
                'customer': str(cart.customer_id),
                'items': [
                    {'product': str(item.product_id), 'quantity': item.quantity}
                    for item in items
                ],
            },
            context={'request': request},
        )
        order_serializer.is_valid(raise_exception=True)
        order = order_serializer.save()
        cart.status = 'converted'
        cart.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

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