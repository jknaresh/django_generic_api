from datetime import date

import pytest
from django.conf import settings

from fixtures.api import (
    api_client,
    user1_token,
    user1,
    profile_record,
    all_perm_token,
    all_perm_user,
)

usage = user1
usage1 = all_perm_user


@pytest.mark.django_db
class TestUserProfileAPI:

    def test_user_profile_fetch_success(
        self, profile_record, api_client, user1_token
    ):
        """
        User fetches profile data successfully
        """

        headers = {"Authorization": f"Bearer {user1_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 200
        assert response_data["data"] == {
            "data": {
                "birthday": date.fromisoformat("2003-04-27"),
                "address": "India",
                "primary_number": "9676416451",
            }
        }
        assert response_data["message"] == "Completed."

    def test_user_null_header(self, api_client):
        """
        User does not pass any header for authentication.
        """

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "User not authenticated."
        assert response_data["code"] == "DGA-V043"

    def test_user_fetch_info_fk_field(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User sends a fk field in profile model to fetch.
        """
        monkeypatch.setattr(
            "django.conf.settings.USER_PROFILE_FIELDS",
            ("gender", "primary_number", "fav_book"),
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 200
        assert response_data["data"] == {
            "data": {
                "gender": "M",
                "primary_number": "9676416451",
                "fav_book_id": 1,
            }
        }
        assert response_data["message"] == "Completed."

    def test_user_wrong_profile_model(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User sends a sets a wrong profile model.
        """
        monkeypatch.setattr(
            "django.conf.settings.USER_PROFILE_MODEL",
            "demo_app.Customer",
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "Invalid profile model"
        assert response_data["code"] == "DGA-S015"

    def test_user_no_profile_model_variable(
        self, api_client, user1_token, monkeypatch
    ):
        """
        User does not set 'USER_PROFILE_MODEL' in settings.
        """
        if hasattr(settings, "USER_PROFILE_MODEL"):
            monkeypatch.delattr(settings, "USER_PROFILE_MODEL")

        headers = {"Authorization": f"Bearer {user1_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert (
            response_data["error"] == "Set setting for 'USER_PROFILE_MODEL'."
        )
        assert response_data["code"] == "DGA-S014"

    def test_user_not_yet_field_names(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User sends a not yet field in settings
        """
        monkeypatch.setattr(
            "django.conf.settings.USER_PROFILE_FIELDS",
            ("ABC", "primary_number", "fav_book"),
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "'[ABC]'s not in the model."
        assert response_data["code"] == "DGA-U006"

    def test_user_profile_not_found(self, api_client, all_perm_token):
        """
        User does not have a related profile
        """

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "User's profile is not found"
        assert response_data["code"] == "DGA-S016"

    def test_user_did_not_set_fetch_fields(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User did not set the USER_PROFILE_FIELDS in settings .
        """
        if hasattr(settings, "USER_PROFILE_FIELDS"):
            monkeypatch.delattr(settings, "USER_PROFILE_FIELDS")

        headers = {"Authorization": f"Bearer {user1_token}"}

        response = api_client.post(
            "/v1/user-profile/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert (
            response_data["error"] == "Set setting for 'USER_PROFILE_FIELDS'."
        )
        assert response_data["code"] == "DGA-S017"
