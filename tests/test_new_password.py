import json
from urllib.parse import quote

import pytest

from fixtures.api import api_client, inactive_user_id, registration_token

BASE_URL = "http://127.0.0.1:8050"


@pytest.mark.django_db
class TestNewPasswordAPI:

    def test_password_reset(
        self, api_client, inactive_user_id, registration_token
    ):
        """
        Successful password reset scenario
        """
        token = registration_token(inactive_user_id)
        encoded_token = quote(token)

        new_password_payload = {
            "payload": {
                "variables": {
                    "password": "test_user@123",
                    "password1": "test_user@123",
                }
            }
        }

        response = api_client.post(
            f"/v1/newpassword/{encoded_token}/",
            new_password_payload,
            format="json",
        )

        response_data = response.data
        assert response.status_code == 200
        assert response_data["message"] == "Your password has been reset."

    def test_invalid_payload_format(
        self, api_client, inactive_user_id, registration_token
    ):
        """
        User has not included a required field in payload.
        """
        token = registration_token(inactive_user_id)
        encoded_token = quote(token)

        new_password_payload = {
            "payload": {
                "variables": {
                    # password field is missing
                    "password1": "test_user@123",
                }
            }
        }

        response = api_client.post(
            f"/v1/newpassword/{encoded_token}/",
            new_password_payload,
            format="json",
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V034"

    def test_extra_field_in_payload(
        self, api_client, inactive_user_id, registration_token
    ):
        """
        User's payload consists an extra field.
        """
        token = registration_token(inactive_user_id)
        encoded_token = quote(token)

        new_password_payload = {
            "payload": {
                "variables": {
                    "password": "test_user@123",
                    "password1": "test_user@123",
                    "extra_field": "ABC",
                }
            }
        }

        response = api_client.post(
            f"/v1/newpassword/{encoded_token}/",
            new_password_payload,
            format="json",
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V034"

    def test_mismatched_password(
        self, api_client, inactive_user_id, registration_token
    ):
        """
        User has given a mismatched password
        """
        token = registration_token(inactive_user_id)
        encoded_token = quote(token)

        new_password_payload = {
            "payload": {
                "variables": {
                    "password": "test_user@12345",
                    "password1": "test_user@123",
                }
            }
        }

        response = api_client.post(
            f"/v1/newpassword/{encoded_token}/",
            new_password_payload,
            format="json",
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["error"] == "passwords does not match"
        assert response_data["code"] == "DGA-V035"

    def test_weak_password(
        self, api_client, inactive_user_id, registration_token
    ):
        """
        Successful password reset scenario
        """
        token = registration_token(inactive_user_id)
        encoded_token = quote(token)

        new_password_payload = {
            "payload": {
                "variables": {
                    "password": "123456",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            f"/v1/newpassword/{encoded_token}/",
            new_password_payload,
            format="json",
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V036"
        assert response_data["error"] == [
            "1. Password must contain at least 8 characters.",
            "2. Password must not be too common.",
            "3. Password must not be entirely numeric.",
        ]

    def test_tampered_token(
        self, api_client, inactive_user_id, registration_token
    ):
        """
        Successful password reset scenario
        """
        new_password_payload = {
            "payload": {
                "variables": {
                    "password": "user123",
                    "password1": "user123",
                }
            }
        }

        response = api_client.post(
            f"/v1/newpassword/MzoxNzMzMTUzMjI6/",  # token is tampered
            new_password_payload,
            format="json",
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V032"
        assert response_data["error"] == "Invalid token format."
