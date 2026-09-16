from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Business, User
from .models import AutomationEvent, AutomationLog, Workflow, WorkflowExecution
from inventory.models import Product


class AutomationTests(APITestCase):
	def setUp(self):
		self.business = Business.objects.create(name='Business', email='business@example.com')
		self.other_business = Business.objects.create(name='Other', email='other@example.com')
		self.user = User.objects.create_user(
			email='owner@example.com', password='password', business=self.business
		)
		self.client.force_authenticate(self.user)
		self.workflow_payload = {
			'name': 'Welcome flow',
			'trigger_type': 'contact.created',
			'definition': {'nodes': [
				{'key': 'welcome', 'action': 'send_whatsapp_message', 'config': {'text': 'Welcome'}},
			]},
		}

	def test_workflow_creation_is_tenant_owned_and_publishable(self):
		response = self.client.post(reverse('workflow-list'), self.workflow_payload, format='json')

		self.assertEqual(response.status_code, 201)
		workflow = Workflow.objects.get()
		self.assertEqual(workflow.business, self.business)
		publish = self.client.post(reverse('workflow-publish', kwargs={'pk': workflow.id}))
		self.assertEqual(publish.status_code, 200)
		workflow.refresh_from_db()
		self.assertEqual(workflow.status, 'active')

	def test_invalid_workflow_action_is_rejected(self):
		payload = {**self.workflow_payload, 'definition': {'nodes': [
			{'key': 'unsafe', 'action': 'execute_python'},
		]}}

		response = self.client.post(reverse('workflow-list'), payload, format='json')

		self.assertEqual(response.status_code, 400)

	def test_event_is_idempotent_and_executes_active_workflow(self):
		workflow = Workflow.objects.create(
			business=self.business,
			name='Welcome flow',
			trigger_type='contact.created',
			definition=self.workflow_payload['definition'],
			status='active',
			created_by=self.user,
		)
		payload = {'event_type': 'contact.created', 'payload': {'contact_id': '1'}}
		first = self.client.post(
			reverse('automation-event'), payload,
			HTTP_IDEMPOTENCY_KEY='event-1', format='json'
		)
		second = self.client.post(
			reverse('automation-event'), payload,
			HTTP_IDEMPOTENCY_KEY='event-1', format='json'
		)

		self.assertEqual(first.status_code, 201)
		self.assertEqual(second.status_code, 200)
		self.assertEqual(AutomationEvent.objects.count(), 1)
		self.assertEqual(WorkflowExecution.objects.count(), 1)
		self.assertEqual(AutomationLog.objects.count(), 1)

	def test_event_endpoint_requires_idempotency_key(self):
		response = self.client.post(reverse('automation-event'), {
			'event_type': 'contact.created', 'payload': {},
		}, format='json')

		self.assertEqual(response.status_code, 400)
		self.assertFalse(AutomationEvent.objects.exists())

	def test_chatbot_works_without_dialogflow_credentials(self):
		response = self.client.post(reverse('dialogflow-webhook'), {
			'text': 'hello', 'session': 'test-session',
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertIn('products', response.data['fulfillmentText'])

	def test_chatbot_product_lookup_is_tenant_scoped(self):
		Product.objects.create(business=self.business, name='Local Flour', price='100.00')
		Product.objects.create(business=Business.objects.create(name='Other', email='other-products@example.com'), name='Hidden Product', price='200.00')

		response = self.client.post(reverse('dialogflow-webhook'), {'text': 'products'}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertIn('Local Flour', response.data['fulfillmentText'])
		self.assertNotIn('Hidden Product', response.data['fulfillmentText'])

# Create your tests here.
