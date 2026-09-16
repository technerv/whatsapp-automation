from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Business, User
from .models import Category, Product


class CatalogueIsolationTests(APITestCase):
	def setUp(self):
		self.first_business = Business.objects.create(
			name='First Business', email='first-business@example.com'
		)
		self.second_business = Business.objects.create(
			name='Second Business', email='second-business@example.com'
		)
		self.user = User.objects.create_user(
			email='owner@example.com', password='Strong-password-123', business=self.first_business
		)
		self.other_user = User.objects.create_user(
			email='other@example.com', password='Strong-password-123', business=self.second_business
		)
		self.client.force_authenticate(self.user)

	def test_product_creation_assigns_authenticated_business(self):
		response = self.client.post(reverse('inventory-product-list'), {
			'name': 'Flour',
			'sku': 'FLOUR-001',
			'price': '250.00',
			'quantity': 10,
		}, format='json')

		self.assertEqual(response.status_code, 201)
		product = Product.objects.get(sku='FLOUR-001')
		self.assertEqual(product.business, self.first_business)
		self.assertEqual(response.data['business'], self.first_business.id)

	def test_product_list_does_not_leak_other_business_data(self):
		Product.objects.create(
			business=self.first_business, name='First Product', price='10.00'
		)
		Product.objects.create(
			business=self.second_business, name='Second Product', price='20.00'
		)

		response = self.client.get(reverse('inventory-product-list'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['name'], 'First Product')

	def test_product_rejects_category_from_another_business(self):
		category = Category.objects.create(business=self.second_business, name='Other')

		response = self.client.post(reverse('inventory-product-list'), {
			'name': 'Hidden Category Product',
			'price': '50.00',
			'category': str(category.id),
		}, format='json')

		self.assertEqual(response.status_code, 400)
