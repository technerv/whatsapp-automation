from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Business, Membership, User
from .permissions import HasBusinessMembership


class TenantMembershipTests(APITestCase):
	def test_registration_creates_business_and_owner_membership(self):
		response = self.client.post(reverse('register'), {
			'email': 'owner@example.com',
			'password': 'Strong-password-123',
			'business_name': 'Owner Business',
		}, format='json')

		self.assertEqual(response.status_code, 201)
		user = User.objects.get(email='owner@example.com')
		self.assertEqual(user.business.name, 'Owner Business')
		self.assertTrue(Membership.objects.filter(
			user=user,
			business=user.business,
			role=Membership.Role.OWNER,
		).exists())

	def test_membership_is_unique_per_business_and_user(self):
		user = User.objects.create_user(email='agent@example.com', password='password')
		business = Business.objects.create(name='Business', email='business@example.com')
		Membership.objects.create(business=business, user=user)

		with self.assertRaises(Exception):
			Membership.objects.create(business=business, user=user)

	def test_permission_rejects_user_from_another_business(self):
		first_business = Business.objects.create(name='First', email='first@example.com')
		second_business = Business.objects.create(name='Second', email='second@example.com')
		user = User.objects.create_user(email='user@example.com', password='password')
		Membership.objects.create(business=first_business, user=user)

		class Resource:
			business_id = second_business.id

		request = self.client.get('/')
		request.user = user
		self.assertFalse(HasBusinessMembership().has_object_permission(request, None, Resource()))
