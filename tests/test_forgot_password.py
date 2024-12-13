import json

import pytest

from fixtures.api import api_client, login_user
from django.core.cache import cache as cache1


# Forgot password test cases use post method for captcha implementation


@pytest.mark.django_db
class TestForgotPasswordAPI:

    def test_success(self, api_client, login_user):
        """
        Success scenario.
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_value = cache1.get(captcha_id)
        assert captcha_value is not None

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_id": captcha_id,
                    "captcha_value": captcha_value,
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert "message" in response_data

    def test_invalid_captcha_id(self, api_client, login_user):
        """
        Invalid captcha id
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_value = cache1.get(captcha_id)
        assert captcha_value is not None

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_id": "81978239-ae63-11ef-8027-e45e375cd493",  # custom UUID 1
                    "captcha_value": captcha_value,
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "CAPTCHA expired or invalid."
        assert response_data["code"] == "DGA-V025"

    def test_invalid_captcha_value(self, api_client, login_user):
        """
        Invalid captcha number
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_value = cache1.get(captcha_id)
        assert captcha_value is not None

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_id": captcha_id,
                    "captcha_value": 1234,
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Invalid CAPTCHA."
        assert response_data["code"] == "DGA-V026"

    def test_invalid_payload_format(self, api_client, login_user):
        """
        Mandatory field is missing in payload
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_value = cache1.get(captcha_id)
        assert captcha_value is not None

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_value": captcha_value,
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V017"

    def test_user_not_found(self, api_client):
        """
        Mandatory field is missing in payload
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_value = cache1.get(captcha_id)
        assert captcha_value is not None

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "nouser@gmail.com",
                    "captcha_id": captcha_id,
                    "captcha_value": captcha_value,
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert response_data["error"] == "User not found"
        assert response_data["code"] == "DGA-V027"

    def test_extra_field_in_payload(self, api_client, login_user):
        """
        User has passed an extra field in payload
        """
        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        assert captcha_response.status_code == 200

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        assert captcha_id is not None

        captcha_value = cache1.get(captcha_id)
        assert captcha_value is not None

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_id": captcha_id,
                    "captcha_value": captcha_value,
                    "extra_field": "ABCD",
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V017"
