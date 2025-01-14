import json
from unittest.mock import patch, MagicMock

import pytest
from django.conf import settings

from fixtures.api import api_client, login_user


@pytest.mark.django_db
class TestLoginAPI:

    def test_login_success(self, api_client, login_user, monkeypatch):
        """
        This is a success scenario for user login .
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "123456"}
            }
        }

        # Sending POST request to login endpoint
        response = api_client.post("/v1/login/", login_payload, format="json")
        response_data = json.loads(response.content.decode("utf-8"))

        # Assertions
        assert response.status_code == 200
        assert "refresh" in response_data["data"][0]
        assert "access" in response_data["data"][0]

    def test_missing_email_property(self, api_client, monkeypatch):
        """
        User has not passed a required field in payload.
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {
                    # missing email
                    "password": "123456",
                }
            }
        }

        response = api_client.post(
            "/v1/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V010"

    def test_invalid_payload_format(self, api_client, login_user, monkeypatch):
        """
        User has given an extra field in payload format.
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "extra_field": "abc",
                    "password": "123456",
                }
            }
        }

        response = api_client.post(
            "/v1/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V010"

    def test_user_does_not_exist(self, api_client, login_user, monkeypatch):
        """
        user has given wrong payload format
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {"email": "abc@gmail.com", "password": "123456"}
            }
        }

        response = api_client.post(
            "/v1/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert response_data["error"] == "Username not found"
        assert response_data["code"] == "DGA-V011"

    def test_invalid_password(self, api_client, login_user, monkeypatch):
        """
        user has given wrong password
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "abcdef"}
            }
        }

        response = api_client.post(
            "/v1/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Invalid password"
        assert response_data["code"] == "DGA-V012"

    def test_login_by_session(self, api_client, login_user, monkeypatch):
        """
        User hits the login API by using session.
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "123456"}
            }
        }

        headers = {"X-Requested-With": "XMLHttpRequest"}
        response = api_client.post(
            "/v1/login/", login_payload, format="json", headers=headers
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Token generation not allowed."
        assert response_data["code"] == "DGA-V021"

    def test_email_invalid_datatype(self, api_client, monkeypatch):
        """
        User sends credentials with wrong data type.
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {"variables": {"email": 123465, "password": "123456"}}
        }
        response = api_client.post(
            "/v1/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Input should be a valid string"
        assert response_data["code"] == "DGA-V010"

    def test_captcha_attributes_sent_captcha_required_true(
        self, api_client, login_user
    ):
        """
        Captcha attributes are sent when CAPTCHA_REQUIRED is True
        """
        # Define the mocked captcha value
        mocked_captcha_value = "ABCD"

        with patch("captcha.models.CaptchaStore.objects.get") as mock_get:
            # Set up the mocked CaptchaStore object
            mock_captcha = MagicMock()
            mock_captcha.challenge = mocked_captcha_value
            mock_get.return_value = mock_captcha

            captcha_response = api_client.post("/v1/generate-captcha/")
            assert captcha_response.status_code == 200
            assert "captcha_key" in captcha_response.data
            assert "captcha_url" in captcha_response.data

            captcha_key = captcha_response.data["captcha_key"]

            login_payload = {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "password": "123456",
                        "captcha_key": captcha_key,
                        "captcha_value": mocked_captcha_value,
                    }
                }
            }

            response = api_client.post(
                "/v1/login/", login_payload, format="json"
            )

            response_data = json.loads(response.content.decode("utf-8"))
            assert response.status_code == 200
            assert "refresh" in response_data["data"][0]
            assert "access" in response_data["data"][0]

    def test_captcha_attributes_not_sent_captcha_required_true(
        self, api_client, login_user
    ):
        """
        Captcha attributes are not sent when CAPTCHA_REQUIRED is True
        """
        login_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "password": "123456",
                }
            }
        }

        response = api_client.post("/v1/login/", login_payload, format="json")

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "Value error, Captcha key and value are required when "
            "`CAPTCHA_REQUIRED` is True."
        )
        assert response_data["code"] == "DGA-V010"

    def test_captcha_attributes_sent_captcha_required_false(
        self, api_client, monkeypatch
    ):
        """
        Captcha attributes are sent when CAPTCHA_REQUIRED is False
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "password": "123456",
                    "captcha_key": "captcha_key",
                    "captcha_value": "mocked_captcha_value",
                }
            }
        }

        response = api_client.post("/v1/login/", login_payload, format="json")

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "Value error, Captcha key and value should not be "
            "provided when `CAPTCHA_REQUIRED` is False."
        )
        assert response_data["code"] == "DGA-V010"

    def test_captcha_attributes_not_sent_captcha_required_false(
        self, api_client, monkeypatch, login_user
    ):
        """
        Captcha attributes are not sent when CAPTCHA_REQUIRED is False
        """
        monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

        assert not settings.CAPTCHA_REQUIRED

        login_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
                    "password": "123456",
                }
            }
        }

        response = api_client.post("/v1/login/", login_payload, format="json")

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert "refresh" in response_data["data"][0]
        assert "access" in response_data["data"][0]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "login_payload, expected_status, expected_keys, expected_error, "
    "expected_code",
    [
        # Test case: Successful login
        (
            {
                "payload": {
                    "variables": {
                        "email": "user@gmail.com",
                        "password": "123456",
                    }
                }
            },
            200,
            ["refresh", "access"],
            None,
            None,
        ),
        # Test case: Missing field in payload
        (
            {
                "payload": {
                    "variables": {
                        "password": "123456",
                    }
                }
            },
            400,
            [],
            "Field required",
            "DGA-V010",
        ),
    ],
)
def test_login(
    api_client,
    login_user,
    login_payload,
    expected_status,
    expected_keys,
    expected_error,
    expected_code,
    monkeypatch,
):
    monkeypatch.setattr("django.conf.settings.CAPTCHA_REQUIRED", False)

    assert not settings.CAPTCHA_REQUIRED

    response = api_client.post("/v1/login/", login_payload, format="json")
    response_data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == expected_status

    if expected_keys:
        for key in expected_keys:
            assert key in response_data["data"][0]

    if expected_error:
        assert response_data["error"] == expected_error
        assert response_data["code"] == expected_code
