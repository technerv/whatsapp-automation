from datetime import date

from django.db import transaction
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from orders.models import Invoice, Order
from .models import Payment
from .serializers import PaymentSerializer
from .services import initiate_stk_push

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(business=self.request.user.business)

    @action(detail=False, methods=['post'], url_path='initiate-mpesa')
    def initiate_mpesa(self, request):
        if not request.user.business_id:
            raise PermissionDenied('Your account is not associated with a business.')
        order_id = request.data.get('order_id')
        phone_number = request.data.get('phone_number')
        if not order_id or not phone_number:
            raise ValidationError({'detail': 'order_id and phone_number are required.'})
        try:
            order = Order.objects.get(id=order_id, business=request.user.business)
        except Order.DoesNotExist as exc:
            raise ValidationError({'order_id': 'Order not found.'}) from exc
        if order.status not in {'new', 'pending_confirmation', 'awaiting_payment'}:
            raise ValidationError({'detail': 'This order cannot receive a payment.'})

        with transaction.atomic():
            invoice, _ = Invoice.objects.get_or_create(
                order=order,
                defaults={'due_date': date.today(), 'amount': order.total_amount},
            )
            payment = Payment.objects.create(
                business=request.user.business,
                invoice=invoice,
                amount=order.total_amount,
                phone_number=phone_number,
            )
            try:
                provider_response = initiate_stk_push(
                    phone_number=phone_number,
                    amount=order.total_amount,
                    order_id=order.id,
                )
            except Exception as exc:
                payment.status = Payment.STATUS_CHOICES[2][0]
                payment.save(update_fields=['status', 'updated_at'])
                raise ValidationError({'detail': str(exc)}) from exc
            payment.merchant_request_id = provider_response.get('MerchantRequestID')
            payment.checkout_request_id = provider_response.get('CheckoutRequestID')
            payment.save(update_fields=['merchant_request_id', 'checkout_request_id', 'updated_at'])
            if order.status != 'awaiting_payment':
                order.transition_to('awaiting_payment')
                order.save(update_fields=['status'])
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def mpesa_callback(request):
    callback = request.data.get('Body', {}).get('stkCallback', {})
    checkout_request_id = callback.get('CheckoutRequestID')
    if not checkout_request_id:
        return JsonResponse({'detail': 'CheckoutRequestID is required.'}, status=400)
    try:
        payment = Payment.objects.select_related('invoice__order').get(
            checkout_request_id=checkout_request_id,
        )
    except Payment.DoesNotExist:
        return JsonResponse({'detail': 'Payment not found.'}, status=404)

    with transaction.atomic():
        payment = Payment.objects.select_for_update().select_related('invoice__order').get(pk=payment.pk)
        if payment.status == 'success':
            return JsonResponse({'status': 'already_processed'})
        payment.callback_payload = request.data
        result_code = callback.get('ResultCode')
        if result_code == 0:
            metadata = {
                item.get('Name'): item.get('Value')
                for item in callback.get('CallbackMetadata', {}).get('Item', [])
            }
            payment.status = 'success'
            payment.transaction_id = metadata.get('MpesaReceiptNumber')
            payment.invoice.status = 'paid'
            payment.invoice.save(update_fields=['status'])
            order = payment.invoice.order
            if order.status == 'awaiting_payment':
                order.transition_to('paid')
                order.save(update_fields=['status'])
        else:
            payment.status = 'failed'
        payment.save(update_fields=['status', 'transaction_id', 'callback_payload', 'updated_at'])
    return JsonResponse({'status': 'processed'})