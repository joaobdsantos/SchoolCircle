from django.test import TestCase


class CoreSmokeTestCase(TestCase):
    def test_healthcheck_endpoint_returns_200(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
