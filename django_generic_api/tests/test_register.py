import pytest
from rest_framework.test import APIClient
import json
from test_support import (
    api_client,
    login_user,
)
from urllib.parse import quote
import time
from unittest import mock


@pytest.mark.django_db
class TestRegisterAPI:

    def test_missing_required_field(self, api_client):
        """
        User has not included a required field in payload.
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "password": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V013"

    def test_extra_field_in_payload(self, api_client):
        """
        User's Register payload consists an extra field.
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "extra_field": "ABCD",
                    "password": "123456",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V013"

    def test_passwords_dont_match(self, api_client):
        """
        User's Register payload does not match predefined payload
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "password": "123456789",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "passwords does not match"
        assert response_data["code"] == "DGA-V014"

    def test_registration_success(self, api_client):
        """
        User registration is success.
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@gmail.com",
                    "password": "123456",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )

        timestamp = int(time.time())
        token = f"{1}:{timestamp}"
        final = quote(token)
        link = f"http://127.0.0.1:8050/api/activate/{final}/"

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["message"] == f"Email sent successfully. {link}"

    def test_invalid_domain(self, api_client):
        """
        User has registered with an invalid domain
        """

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@abcdef.com",
                    "password": "123456",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Invalid email domain"
        assert response_data["code"] == "DGA-V022"

    def test_email_already_exist(self, api_client, login_user):
        """
        User registers with an existing email.
        """

        register_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "password": "123456",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"] == "Account already exists with this email."
        )
        assert response_data["code"] == "DGA-V015"
