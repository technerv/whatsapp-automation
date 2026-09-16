from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Business, User
from crm.models import Customer
from inventory.models import Product
from .models import Cart, CartItem, Order


class OrderLifecycleTests(APITestCase):
	def setUp(self):
		self.first_business = Business.objects.create(name='First', email='first@example.com')
		self.second_business = Business.objects.create(name='Second', email='second@example.com')
		self.user = User.objects.create_user(
			email='owner@example.com', password='password', business=self.first_business
		)
		self.customer = Customer.objects.create(
			business=self.first_business, name='Customer', phone_number='+254700000001'
		)
		self.product = Product.objects.create(
			business=self.first_business, name='Product', price='100.00', quantity=5
		)
		self.client.force_authenticate(self.user)

	def test_create_order_snapshots_price_calculates_total_and_reserves_stock(self):
		response = self.client.post(reverse('order-list'), {
			'customer': str(self.customer.id),
			'items': [{'product': str(self.product.id), 'quantity': 2}],
		}, format='json')

		self.assertEqual(response.status_code, 201)
		order = Order.objects.get()
		self.assertEqual(order.status, Order.STATUS_CHOICES[0][0])
		self.assertEqual(order.total_amount, Decimal('200.00'))
		self.assertEqual(order.items.get().price, Decimal('100.00'))
		self.product.refresh_from_db()
		self.assertEqual(self.product.quantity, 3)

	def test_order_rejects_insufficient_stock_without_creating_order(self):
		response = self.client.post(reverse('order-list'), {
			'customer': str(self.customer.id),
			'items': [{'product': str(self.product.id), 'quantity': 6}],
		}, format='json')

		self.assertEqual(response.status_code, 400)
		self.assertFalse(Order.objects.exists())

	def test_order_cannot_use_customer_from_another_business(self):
		other_customer = Customer.objects.create(
			business=self.second_business, name='Other', phone_number='+254700000002'
		)

		response = self.client.post(reverse('order-list'), {
			'customer': str(other_customer.id),
			'items': [{'product': str(self.product.id), 'quantity': 1}],
		}, format='json')

		self.assertEqual(response.status_code, 400)

	def test_order_status_transitions_are_enforced(self):
		order = Order.objects.create(
			business=self.first_business, customer=self.customer, created_by=self.user
		)

		valid = self.client.post(reverse('order-transition', kwargs={'pk': order.id}), {
			'status': 'pending_confirmation',
		}, format='json')
		invalid = self.client.post(reverse('order-transition', kwargs={'pk': order.id}), {
			'status': 'delivered',
		}, format='json')

		self.assertEqual(valid.status_code, 200)
		self.assertEqual(invalid.status_code, 400)


class CartTests(APITestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Cart Business', email='cart@example.com')
		self.user = User.objects.create_user(
			email='cart-owner@example.com', password='password', business=self.business
		)
		self.customer = Customer.objects.create(
			business=self.business, name='Cart Customer', phone_number='+254700000010'
		)
		self.product = Product.objects.create(
			business=self.business, name='Cart Product', price='75.00', quantity=4
		)
		self.client.force_authenticate(self.user)

	def test_cart_add_item_and_checkout_creates_order(self):
		cart_response = self.client.post(reverse('cart-list'), {
			'customer': str(self.customer.id),
		}, format='json')
		cart_id = cart_response.data['id']

		item_response = self.client.post(reverse('cart-add-item', kwargs={'pk': cart_id}), {
			'product': str(self.product.id), 'quantity': 2,
		}, format='json')
		checkout = self.client.post(reverse('cart-checkout', kwargs={'pk': cart_id}))

		self.assertEqual(cart_response.status_code, 201)
		self.assertEqual(item_response.status_code, 200)
		self.assertEqual(checkout.status_code, 201)
		self.assertEqual(Order.objects.count(), 1)
		self.assertEqual(Order.objects.get().total_amount, Decimal('150.00'))
		self.assertEqual(Cart.objects.get().status, 'converted')
		self.product.refresh_from_db()
		self.assertEqual(self.product.quantity, 2)

	def test_empty_cart_cannot_checkout(self):
		cart = Cart.objects.create(business=self.business, customer=self.customer)

		response = self.client.post(reverse('cart-checkout', kwargs={'pk': cart.id}))

		self.assertEqual(response.status_code, 400)
		self.assertFalse(Order.objects.exists())
