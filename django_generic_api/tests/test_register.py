import json

import pytest

from fixtures.API import api_client, login_user
from django.core.cache import cache as cache1


@pytest.mark.django_db
class TestRegisterAPI:

    def test_registration_success(self, api_client):
        """
        User registration is success.
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@gmail.com",
                    "password": "test_user@123",
                    "password1": "test_user@123",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert "message" in response_data

    def test_registration_weak_password(self, api_client):
        """
        User registration is success.
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@gmail.com",
                    "password": "123456",
                    "password1": "123456",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == [
            "1. Password must contain at least 8 characters.",
            "2. Password must not be too common.",
            "3. Password must not be entirely numeric.",
        ]
        assert response_data["code"] == "DGA-V024"

    def test_invalid_payload_format(self, api_client):
        """
        User has not included a required field in payload.
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "password": "123456",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
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
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "extra_field": "ABCD",
                    "password": "123456",
                    "password1": "123456",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V013"
        assert response_data["error"] == "Extra inputs are not permitted"

    def test_passwords_dont_match(self, api_client):
        """
        User's Register payload does not match predefined payload
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "password": "123456789",
                    "password1": "123456",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "passwords does not match"
        assert response_data["code"] == "DGA-V014"

    def test_invalid_domain(self, api_client):
        """
        User has registered with an invalid domain
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@abcdef.com",
                    "password": "test_user@123",
                    "password1": "test_user@123",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
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
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "password": "test_user@123",
                    "password1": "test_user@123",
                    "captcha_id": captcha_id,
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"] == "Account already exists with this email."
        )
        assert response_data["code"] == "DGA-V015"

    def test_invalid_captcha_number(self, api_client):
        """
        User registration is success.
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@gmail.com",
                    "password": "test_user@123",
                    "password1": "test_user@123",
                    "captcha_id": captcha_id,
                    "captcha_number": 1234,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Invalid CAPTCHA."
        assert response_data["code"] == "DGA-V030"

    def test_invalid_captcha_id(self, api_client):
        """
        User registration is success.
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_number = cache1.get(captcha_id)
        assert captcha_number is not None

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@gmail.com",
                    "password": "test_user@123",
                    "password1": "test_user@123",
                    "captcha_id": "81978239-ae63-11ef-8027-e45e375cd493",  # custom UUID 1
                    "captcha_number": captcha_number,
                }
            }
        }

        response = api_client.post(
            "/register/",
            register_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "CAPTCHA expired or invalid."
        assert response_data["code"] == "DGA-V029"
