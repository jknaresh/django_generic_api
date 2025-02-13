import base64
import time

import pytest
from django.contrib.auth.models import User

from fixtures.api import (
    api_client,
    non_existing_user,
    inactive_user_id,
)

# To ensure the import is retained
usage = non_existing_user


@pytest.mark.django_db
class TestAccountActivateAPI:

    def test_expired_activation_link(self, api_client, inactive_user_id):
        """
        User's activation link is expired.
        """
        timestamp = int(time.time()) - (25 * 60 * 60)  # 25 hours old timestamp
        token = f"{inactive_user_id}:{timestamp}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()

        response = api_client.get(
            f"/v1/activate/{encoded_token}/",
            format="json",
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "The activation link has expired."
        assert response_data["code"] == "DGA-V028"

    def test_email_is_already_active(self, api_client, inactive_user_id):
        """
        User is already active.
        """

        user = User.objects.get(id=inactive_user_id)
        user.is_active = True
        user.save()

        timestamp = int(time.time())
        token = f"{user.id}:{timestamp}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()

        response = api_client.get(
            f"/v1/activate/{encoded_token}/",
            format="json",
        )

        response_data = response.data
        assert response.status_code == 200
        assert response_data["message"] == "Account is already active."

    def test_user_does_not_exist(self, api_client, inactive_user_id):
        """
        User id does not exist
        """
        user = User.objects.get(id=inactive_user_id)

        timestamp = int(time.time())
        token = f"{user.id}:{timestamp}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()
        user.delete()

        response = api_client.get(
            f"/v1/activate/{encoded_token}/",
            format="json",
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["error"] == "User not found."
        assert response_data["code"] == "DGA-V029"

    def test_user_activated_success(self, api_client, inactive_user_id):
        """
        User account is activated successfully.
        """
        timestamp = int(time.time())
        token = f"{inactive_user_id}:{timestamp}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()

        response = api_client.get(
            f"/v1/activate/{encoded_token}/",
            format="json",
        )

        response_data = response.data
        assert response.status_code == 201
        assert (
            response_data["message"]
            == "Your account has been activated successfully."
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "setup_user, expected_status, expected_message, expected_error, "
    "expected_code",
    [
        # Test case: User account is activated successfully
        (
            "inactive_user_id",
            201,
            "Your account has been activated successfully.",
            None,
            None,
        ),
        # Test case: User does not exist
        (
            "non_existing_user",
            400,
            None,
            "User not found.",
            "DGA-V029",
        ),
    ],
)
def test_activate_user(
    request,
    api_client,
    setup_user,
    expected_status,
    expected_message,
    expected_error,
    expected_code,
):
    # Retrieve or prepare user ID based on the setup fixture
    user_id = request.getfixturevalue(setup_user)

    token = f"{user_id}:{int(time.time())}"
    encoded_token = base64.urlsafe_b64encode(token.encode()).decode()

    response = api_client.get(f"/v1/activate/{encoded_token}/", format="json")
    response_data = response.data

    assert response.status_code == expected_status

    if expected_message:
        assert response_data["message"] == expected_message
    if expected_error:
        assert response_data["error"] == expected_error
        assert response_data["code"] == expected_code
