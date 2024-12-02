import json

import pytest

from fixtures.API import api_client, login_user


@pytest.mark.django_db
class TestLoginAPI:

    def test_login_success(self, api_client, login_user):
        """
        This is a success scenario for user login .
        """
        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "123456"}
            }
        }

        # Sending POST request to login endpoint
        response = api_client.post("/login/", login_payload, format="json")
        response_data = json.loads(response.content.decode("utf-8"))

        # Assertions
        assert response.status_code == 200
        assert "refresh" in response_data["data"][0]
        assert "access" in response_data["data"][0]

    def test_missing_email_property(self, api_client):
        """
        User has not passed a required field in payload.
        """
        login_payload = {
            "payload": {
                "variables": {
                    # missing email
                    "password": "123456",
                }
            }
        }

        response = api_client.post(
            "/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V010"

    def test_invalid_payload_format(self, api_client, login_user):
        """
        User has given an extra field in payload format.
        """

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
            "/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V010"

    def test_user_does_not_exist(self, api_client, login_user):
        """
        user has given wrong payload format
        """

        login_payload = {
            "payload": {
                "variables": {"email": "abc@gmail.com", "password": "123456"}
            }
        }

        response = api_client.post(
            "/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert response_data["error"] == "Username not found"
        assert response_data["code"] == "DGA-V011"

    def test_invalid_password(self, api_client, login_user):
        """
        user has given wrong password
        """

        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "abcdef"}
            }
        }

        response = api_client.post(
            "/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Invalid password"
        assert response_data["code"] == "DGA-V012"

    def test_login_by_session(self, api_client, login_user):
        """
        User hits the login API by using session.
        """
        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "123456"}
            }
        }

        headers = {"X-Requested-With": "XMLHttpRequest"}
        response = api_client.post(
            "/login/", login_payload, format="json", headers=headers
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Token generation not allowed."
        assert response_data["code"] == "DGA-V021"

    def test_email_invalid_datatype(self, api_client):
        """
        User sends credentials with wrong data type.
        """
        login_payload = {
            "payload": {"variables": {"email": 123465, "password": "123456"}}
        }
        response = api_client.post(
            "/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Input should be a valid string"
        assert response_data["code"] == "DGA-V010"


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
):
    response = api_client.post("/login/", login_payload, format="json")
    response_data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == expected_status

    if expected_keys:
        for key in expected_keys:
            assert key in response_data["data"][0]

    if expected_error:
        assert response_data["error"] == expected_error
        assert response_data["code"] == expected_code
