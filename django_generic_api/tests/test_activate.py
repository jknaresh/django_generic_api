import pytest
from rest_framework.test import APIClient
import json
from test_support import (
    api_client,
    email_activate_inactive_user_id,
)
import time
from django.contrib.auth.models import User
from unittest import mock
from rest_framework_simplejwt.tokens import AccessToken


@pytest.mark.django_db
class TestAccountActivateAPI:

    def test_expired_activation_link(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User's activation link is expired.
        """
        timestamp = int(time.time()) - (25 * 60 * 60)  # 25 hours old timestamp
        token = f"{email_activate_inactive_user_id}:{timestamp}"

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "The activation link has expired."
        assert response_data["code"] == "DGA-V018"

    def test_email_is_already_active(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User is already active.
        """

        user = User.objects.get(id=email_activate_inactive_user_id)
        user.is_active = True
        user.save()

        timestamp = int(time.time())
        token = f"{user.id}:{timestamp}"

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["message"] == "Account is already active."

    def test_user_does_not_exist(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User id does not exist
        """
        user = User.objects.get(id=email_activate_inactive_user_id)

        timestamp = int(time.time())
        token = f"{user.id}:{timestamp}"
        user.delete()

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "User not found."
        assert response_data["code"] == "DGA-V019"

    def test_user_activated_success(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User account is activated successfully.
        """
        timestamp = int(time.time())
        token = f"{email_activate_inactive_user_id}:{timestamp}"

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert (
            response_data["message"]
            == "Your account has been activated successfully."
        )