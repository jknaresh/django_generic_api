import json
import pytest
from unittest.mock import patch, MagicMock

from fixtures.api import api_client, login_user
from captcha.models import CaptchaStore

# Forgot password test cases use post method for captcha implementation


@pytest.mark.django_db
class TestForgotPasswordAPI:

    def test_success_with_mocked_captcha_value(self, api_client, login_user):
        """
        Test successful captcha validation by mocking only the captcha_value.
        """
        # Define the mocked captcha value
        mocked_captcha_value = "ABCD"

        with patch("captcha.models.CaptchaStore.objects.get") as mock_get:
            # Set up the mocked CaptchaStore object
            mock_captcha = MagicMock()
            mock_captcha.response = mocked_captcha_value.lower()
            mock_get.return_value = mock_captcha

            captcha_response = api_client.post("/generate_captcha/")
            assert captcha_response.status_code == 200
            assert "captcha_key" in captcha_response.data
            assert "image_url" in captcha_response.data

            captcha_key = captcha_response.data["captcha_key"]

            forgot_password_payload = {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
                    }
                }
            }

            response = api_client.post(
                "/forgotPassword/",
                forgot_password_payload,
                format="json",
            )

            response_data = response.json()

            # Assertions
            assert response.status_code == 200
            assert "message" in response_data

    def test_failure_with_invalid_captcha_key(self, api_client):
        """
        Test failure when captcha_key is invalid (empty CaptchaStore.objects).
        """

        with patch("captcha.models.CaptchaStore.objects.get") as mock_get:
            mock_get.side_effect = CaptchaStore.DoesNotExist

            captcha_response = api_client.post("/generate_captcha/")
            assert captcha_response.status_code == 200
            assert "captcha_key" in captcha_response.data
            assert "image_url" in captcha_response.data

            # Use the mocked behavior for invalid captcha key
            captcha_key = captcha_response.data["captcha_key"]
            forgot_password_payload = {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "captcha_key": captcha_key,
                        "captcha_value": "ABCD",
                    }
                }
            }

            # Simulate a request to validate the captcha
            response = api_client.post(
                "/forgotPassword/",
                forgot_password_payload,
                format="json",
            )

            response_data = response.json()

            # Assertions
            assert response.status_code == 400
            assert response_data["error"] == "Invalid or expired captcha key."
            assert response_data["code"] == "DGA-V036"

    def test_invalid_captcha_value(self, api_client, login_user):
        """
        Invalid captcha number
        """
        mocked_captcha_value = "ABCD"

        with patch("captcha.models.CaptchaStore.objects.get") as mock_get:
            # Set up the mocked CaptchaStore object
            mock_captcha = MagicMock()
            mock_captcha.response = mocked_captcha_value.lower()
            mock_get.return_value = mock_captcha

            captcha_response = api_client.post("/generate_captcha/")
            assert captcha_response.status_code == 200
            assert "captcha_key" in captcha_response.data
            assert "image_url" in captcha_response.data

            # Use the mocked captcha value for testing
            captcha_key = captcha_response.data["captcha_key"]
            forgot_password_payload = {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "captcha_key": captcha_key,
                        "captcha_value": "HELO",
                    }
                }
            }

            response = api_client.post(
                "/forgotPassword/",
                forgot_password_payload,
                format="json",
            )

            response_data = response.json()

            # Assertions
            assert response.status_code == 400
            assert response_data["error"] == "Invalid captcha response."
            assert response_data["code"] == "DGA-V026"

    def test_invalid_payload_format(self, api_client, login_user):
        """
        Mandatory field is missing in payload
        """

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_value": "ABCD",
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
        mocked_captcha_value = "ABCD"

        with patch("captcha.models.CaptchaStore.objects.get") as mock_get:
            # Set up the mocked CaptchaStore object
            mock_captcha = MagicMock()
            mock_captcha.response = mocked_captcha_value.lower()
            mock_get.return_value = mock_captcha

            captcha_response = api_client.post("/generate_captcha/")
            assert captcha_response.status_code == 200
            assert "captcha_key" in captcha_response.data
            assert "image_url" in captcha_response.data

            # Use the mocked captcha value for testing
            captcha_key = captcha_response.data["captcha_key"]
            forgot_password_payload = {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
                    }
                }
            }

            response = api_client.post(
                "/forgotPassword/",
                forgot_password_payload,
                format="json",
            )

            response_data = response.json()

            assert response.status_code == 404
            assert response_data["error"] == "User not found"
            assert response_data["code"] == "DGA-V037"

    def test_extra_field_in_payload(self, api_client, login_user):
        """
        User has passed an extra field in payload
        """

        forgot_password_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "captcha_key": "captcha_id",
                    "captcha_value": "ABCD",
                    "extra_field": "ABCD",
                }
            }
        }

        response = api_client.post(
            "/forgotPassword/",
            forgot_password_payload,
            format="json",
        )

        response_data = response.json()

        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V017"
