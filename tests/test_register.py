import json
from unittest.mock import patch, MagicMock
import pytest

from fixtures.api import api_client, login_user
from captcha.models import CaptchaStore

# Register test cases use post method for captcha implementation


@pytest.mark.django_db
class TestRegisterAPI:

    def test_registration_success(self, api_client):
        """
        User registration is success.
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "abc@gmail.com",
                        "password": "test_user@123",
                        "password1": "test_user@123",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "abc@gmail.com",
                        "password": "123456",
                        "password1": "123456",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "ab@gmail.com",
                        "password": "123456",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "ab@gmail.com",
                        "extra_field": "ABCD",
                        "password": "123456",
                        "password1": "123456",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "ab@gmail.com",
                        "password": "123456789",
                        "password1": "123456",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "abc@abcdef.com",
                        "password": "test_user@123",
                        "password1": "test_user@123",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "password": "test_user@123",
                        "password1": "test_user@123",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
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
                response_data["error"]
                == "Account already exists with this email."
            )
            assert response_data["code"] == "DGA-V015"

    def test_invalid_captcha_value(self, api_client):
        """
        User registration is success.
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

            captcha_key = captcha_response.data["captcha_key"]

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "abc@gmail.com",
                        "password": "test_user@123",
                        "password1": "test_user@123",
                        "captcha_key": captcha_key,
                        "captcha_value": "1234",
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
            assert response_data["error"] == "Invalid captcha response."
            assert response_data["code"] == "DGA-V025"

    def test_invalid_captcha_id(self, api_client):
        """
        User registration is success.
        """
        with patch("captcha.models.CaptchaStore.objects.get") as mock_get:
            mock_get.side_effect = CaptchaStore.DoesNotExist

            captcha_response = api_client.post("/generate_captcha/")
            assert captcha_response.status_code == 200
            assert "captcha_key" in captcha_response.data
            assert "image_url" in captcha_response.data

            # Use the mocked behavior for invalid captcha key
            captcha_key = captcha_response.data["captcha_key"]

            register_payload = {
                "payload": {
                    "variables": {
                        "email": "abc@gmail.com",
                        "password": "test_user@123",
                        "password1": "test_user@123",
                        "captcha_key": captcha_key,
                        "captcha_value": "ABCD",
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
            assert response_data["error"] == "Invalid or expired captcha key."
            assert response_data["code"] == "DGA-V027"
