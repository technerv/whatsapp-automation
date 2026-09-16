from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse('healthz'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_readiness_endpoint(self):
        response = self.client.get(reverse('readyz'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'database': 'ok'})
