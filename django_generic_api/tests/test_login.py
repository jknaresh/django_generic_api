import pytest
from rest_framework.test import APIClient
import json
from test_support import (
    api_client,
    login_user,
)
from django.contrib.auth.models import User
from unittest import mock


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
        response = api_client.post("/api/login/", login_payload, format="json")
        response_data = json.loads(response.content.decode("utf-8"))

        # Assertions
        assert response.status_code == 200
        assert "refresh" in response_data["data"][0]
        assert "access" in response_data["data"][0]

    def test_missing_field_in_payload(self, api_client):
        """
        User has not passed a required field in payload.
        """
        login_payload = {
            "payload": {
                "variables": {
                    "password": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V010"

    def test_extra_field_in_payload_format(self, api_client):
        """
        User has given an extra field in payload format.
        """

        login_payload = {
            "payload": {
                "variables": {
                    "email": "admin",
                    "extra_field": "abc",
                    "password": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/login/",
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
            "/api/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert response_data["error"] == "Username not found"
        assert response_data["code"] == "DGA-V011"

    def test_wrong_password(self, api_client, login_user):
        """
        user has given wrong password
        """

        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "abcdef"}
            }
        }

        response = api_client.post(
            "/api/login/",
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
            "/api/login/", login_payload, format="json", headers=headers
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Token generation not allowed."
        assert response_data["code"] == "DGA-V021"

    def test_login_credentials_invalid_datatype(self, api_client):
        """
        User sends credentials with wrong data type.
        """
        login_payload = {
            "payload": {"variables": {"email": 123465, "password": "123456"}}
        }
        response = api_client.post(
            "/api/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Input should be a valid string"
        assert response_data["code"] == "DGA-V010"
