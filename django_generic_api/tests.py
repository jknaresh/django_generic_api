from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from your_app.models import Contact  # Import your models here


class GenericFetchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()

        # Create sample data for fetch
        self.user = self.user_model.objects.create(
            first_name="John", last_name="Doe", email="john.doe@example.com"
        )
        self.contact = Contact.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            organization_id="org123",
        )

    def test_fetch_user_data(self):
        """Test fetching user data using modelName and filters."""
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "user",
                    "fields": ["first_name", "last_name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "email",
                            "value": ["john.doe@example.com"],
                        }
                    ],
                }
            }
        }

        response = self.client.post(
            "/api/fetch/", fetch_payload, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"][0]["first_name"], "John")
        self.assertEqual(response.data["data"][0]["last_name"], "Doe")

    def test_fetch_contact_data(self):
        """Test fetching contact data using modelName and fields."""
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "contact",
                    "fields": ["first_name", "last_name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "email",
                            "value": ["jane.doe@example.com"],
                        }
                    ],
                }
            }
        }

        response = self.client.post(
            "/api/fetch/", fetch_payload, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"][0]["first_name"], "Jane")
        self.assertEqual(response.data["data"][0]["last_name"], "Doe")
