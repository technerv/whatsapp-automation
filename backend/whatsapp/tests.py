from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Business, Membership, User
from crm.models import Customer
from .models import Conversation, WhatsAppAccount, WhatsAppMessage, WebhookEvent


class WhatsAppWebhookTests(APITestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Business', email='business@example.com')
		self.account = WhatsAppAccount.objects.create(
			business=self.business,
			phone_number_id='phone-number-1',
			business_account_id='business-account-1',
		)
		self.url = reverse('whatsapp-webhook')
		self.payload = {
			'entry': [{
				'changes': [{
					'value': {
						'metadata': {'phone_number_id': 'phone-number-1'},
						'contacts': [{'wa_id': '254700000001', 'profile': {'name': 'Jane'}}],
						'messages': [{
							'id': 'wamid-1',
							'from': '254700000001',
							'type': 'text',
							'text': {'body': 'I want flour'},
						}],
					},
				}],
			}],
		}

	@override_settings(WHATSAPP_VERIFY_TOKEN='verify-token')
	def test_meta_verification_returns_challenge(self):
		response = self.client.get(self.url, {
			'hub.mode': 'subscribe',
			'hub.verify_token': 'verify-token',
			'hub.challenge': 'challenge-value',
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data, 'challenge-value')

	def test_inbound_message_creates_customer_conversation_and_message(self):
		response = self.client.post(self.url, self.payload, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(Customer.objects.get().business, self.business)
		self.assertEqual(Conversation.objects.count(), 1)
		self.assertEqual(WhatsAppMessage.objects.get().content, 'I want flour')
		self.assertEqual(WebhookEvent.objects.get().status, 'processed')

	def test_duplicate_webhook_is_idempotent(self):
		first = self.client.post(self.url, self.payload, format='json')
		second = self.client.post(self.url, self.payload, format='json')

		self.assertEqual(first.status_code, 200)
		self.assertEqual(second.status_code, 200)
		self.assertEqual(WhatsAppMessage.objects.count(), 1)
		self.assertEqual(WebhookEvent.objects.count(), 1)


class InboxCollaborationTests(APITestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Inbox Business', email='inbox@example.com')
		self.other_business = Business.objects.create(name='Other Business', email='other-inbox@example.com')
		self.user = User.objects.create_user(email='agent@example.com', password='password', business=self.business)
		self.other_user = User.objects.create_user(email='other-agent@example.com', password='password', business=self.other_business)
		Membership.objects.create(business=self.business, user=self.user, role=Membership.Role.AGENT)
		self.customer = Customer.objects.create(business=self.business, name='Jane Inbox', phone_number='+254700000099')
		self.conversation = Conversation.objects.create(business=self.business, customer=self.customer, unread_count=2)
		self.client.force_authenticate(self.user)

	def test_search_and_status_filter_are_tenant_scoped(self):
		response = self.client.get(reverse('conversation-list'), {'search': 'Jane', 'status': 'open'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 1)

	def test_assign_requires_active_member_of_same_business(self):
		response = self.client.post(reverse('conversation-assign', kwargs={'pk': self.conversation.id}), {
			'user_id': str(self.other_user.id),
		}, format='json')

		self.assertEqual(response.status_code, 400)

	def test_status_and_mark_read_actions(self):
		status_response = self.client.post(reverse('conversation-status', kwargs={'pk': self.conversation.id}), {
			'status': 'pending',
		}, format='json')
		read_response = self.client.post(reverse('conversation-mark-read', kwargs={'pk': self.conversation.id}))

		self.assertEqual(status_response.status_code, 200)
		self.assertEqual(read_response.status_code, 200)
		self.conversation.refresh_from_db()
		self.assertEqual(self.conversation.status, 'pending')
		self.assertEqual(self.conversation.unread_count, 0)
