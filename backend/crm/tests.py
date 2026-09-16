from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import Business, User
from .models import Customer, Lead


class CRMIsolationTests(APITestCase):
	def setUp(self):
		self.first_business = Business.objects.create(
			name='First Business', email='first@example.com'
		)
		self.second_business = Business.objects.create(
			name='Second Business', email='second@example.com'
		)
		self.user = User.objects.create_user(
			email='first-user@example.com', password='password', business=self.first_business
		)
		self.other_user = User.objects.create_user(
			email='second-user@example.com', password='password', business=self.second_business
		)
		self.client.force_authenticate(self.user)

	def test_customer_creation_assigns_authenticated_business(self):
		response = self.client.post(reverse('customer-list'), {
			'name': 'Jane Customer',
			'phone_number': '+254700000001',
		}, format='json')

		self.assertEqual(response.status_code, 201)
		customer = Customer.objects.get(phone_number='+254700000001')
		self.assertEqual(customer.business, self.first_business)
		self.assertEqual(response.data['business'], self.first_business.id)

	def test_customer_phone_can_repeat_across_businesses_but_not_within_one(self):
		Customer.objects.create(
			business=self.first_business, name='First', phone_number='+254700000002'
		)
		Customer.objects.create(
			business=self.second_business, name='Second', phone_number='+254700000002'
		)

		response = self.client.post(reverse('customer-list'), {
			'name': 'Duplicate First',
			'phone_number': '+254700000002',
		}, format='json')

		self.assertEqual(response.status_code, 400)

	def test_dashboard_counts_only_authenticated_business(self):
		Customer.objects.create(
			business=self.first_business, name='First', phone_number='+254700000003'
		)
		Customer.objects.create(
			business=self.second_business, name='Second', phone_number='+254700000004'
		)
		Lead.objects.create(
			business=self.second_business, name='Other Lead', phone_number='+254700000005'
		)

		response = self.client.get(reverse('dashboard-stats'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), {'customer_count': 1, 'lead_count': 0})

	def test_dashboard_endpoints_require_authentication(self):
		self.client.force_authenticate(user=None)

		response = self.client.get(reverse('dashboard-stats'))

		self.assertEqual(response.status_code, 401)
