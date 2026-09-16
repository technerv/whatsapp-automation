from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Business, User
from crm.models import Customer
from inventory.models import Product
from orders.models import Order
from .models import Payment


class MpesaPaymentTests(APITestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Business', email='business@example.com')
		self.user = User.objects.create_user(
			email='owner@example.com', password='password', business=self.business
		)
		customer = Customer.objects.create(
			business=self.business, name='Customer', phone_number='+254700000001'
		)
		self.order = Order.objects.create(
			business=self.business, customer=customer, created_by=self.user,
			status='awaiting_payment', total_amount=Decimal('250.00')
		)
		self.client.force_authenticate(self.user)

	@patch('payments.views.initiate_stk_push')
	def test_stk_initiation_creates_pending_payment_only(self, initiate):
		initiate.return_value = {
			'MerchantRequestID': 'merchant-1', 'CheckoutRequestID': 'checkout-1'
		}

		response = self.client.post(reverse('payment-initiate-mpesa'), {
			'order_id': str(self.order.id), 'phone_number': '+254700000001'
		}, format='json')

		self.assertEqual(response.status_code, 201)
		payment = Payment.objects.get()
		self.assertEqual(payment.status, 'pending')
		self.assertEqual(payment.checkout_request_id, 'checkout-1')
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, 'awaiting_payment')

	@patch('payments.views.initiate_stk_push')
	def test_success_callback_marks_payment_and_order_paid(self, initiate):
		initiate.return_value = {'CheckoutRequestID': 'checkout-2'}
		self.client.post(reverse('payment-initiate-mpesa'), {
			'order_id': str(self.order.id), 'phone_number': '+254700000001'
		}, format='json')
		callback = {'Body': {'stkCallback': {
			'CheckoutRequestID': 'checkout-2', 'ResultCode': 0,
			'CallbackMetadata': {'Item': [{'Name': 'MpesaReceiptNumber', 'Value': 'ABC123'}]},
		}}}

		response = self.client.post(reverse('payments-mpesa-callback'), callback, format='json')

		self.assertEqual(response.status_code, 200)
		payment = Payment.objects.get()
		self.assertEqual(payment.status, 'success')
		self.assertEqual(payment.transaction_id, 'ABC123')
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, 'paid')

	@patch('payments.views.initiate_stk_push')
	def test_duplicate_success_callback_is_idempotent(self, initiate):
		initiate.return_value = {'CheckoutRequestID': 'checkout-3'}
		self.client.post(reverse('payment-initiate-mpesa'), {
			'order_id': str(self.order.id), 'phone_number': '+254700000001'
		}, format='json')
		callback = {'Body': {'stkCallback': {'CheckoutRequestID': 'checkout-3', 'ResultCode': 0}}}

		first = self.client.post(reverse('payments-mpesa-callback'), callback, format='json')
		second = self.client.post(reverse('payments-mpesa-callback'), callback, format='json')

		self.assertEqual(first.status_code, 200)
		self.assertEqual(second.status_code, 200)
		self.assertEqual(Payment.objects.get().status, 'success')

# Create your tests here.
