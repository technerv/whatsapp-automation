from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Business
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
