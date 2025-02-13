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

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["birthday", "gender", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 200
        assert response_data["data"]["data"] == [
            {
                "birthday": date.fromisoformat("2003-04-27"),
                "gender": "M",
                "primary_number": "9676416451",
            }
        ]
        assert response_data["message"] == "Completed."

    def test_user_null_header(self, api_client):
        """
        User does not pass any header for authentication.
        """

        response = api_client.post(
            "/v1/1-1/",
            format="json",
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "User not authenticated."
        assert response_data["code"] == "DGA-V040"

    def test_user_fetch_info_fk_field(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User sends a fk field in profile model to fetch.
        """
        monkeypatch.setitem(
            settings.ONE_TO_ONE_MODELS["demo_app.UserProfile"],
            "fetch_fields",
            ("fav_book__id", "address", "primary_number"),
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["fav_book__id", "address", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 200
        assert response_data["data"]["data"] == [
            {
                "address": "India",
                "primary_number": "9676416451",
                "fav_book__id": 1,
            }
        ]
        assert response_data["message"] == "Completed."

    def test_user_wrong_profile_model(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User sends a sets a wrong profile model.
        """
        monkeypatch.setattr(
            settings,
            "ONE_TO_ONE_MODELS",
            {
                "demo_app.Customer": {
                    "user_related_field": "user",
                    "fetch_fields": ("birthday", "gender", "primary_number"),
                    "save_fields": ("birthday", "gender", "primary_number"),
                }
            },
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["birthday", "gender", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert (
            response_data["error"] == "demo_app.UserProfile is not configured."
        )
        assert response_data["code"] == "DGA-S020"

    def test_user_no_profile_model_variable(
        self, api_client, user1_token, monkeypatch
    ):
        """
        System settings does not have ONE_TO_ONE_MODEL settings.
        """
        if hasattr(settings, "ONE_TO_ONE_MODELS"):
            monkeypatch.delattr(settings, "ONE_TO_ONE_MODELS")

        headers = {"Authorization": f"Bearer {user1_token}"}

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["birthday", "gender", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert (
            response_data["error"] == "Set settings for User Related models."
        )
        assert response_data["code"] == "DGA-S019"

    def test_user_not_yet_field_names(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        System has set with not yet fields.
        """
        monkeypatch.setitem(
            settings.ONE_TO_ONE_MODELS["demo_app.UserProfile"],
            "fetch_fields",
            ("birthday", "gender", "ABCD"),
        )
        headers = {"Authorization": f"Bearer {user1_token}"}

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["birthday", "gender", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "Extra field {'ABCD'}"
        assert response_data["code"] == "DGA-U002"

    def test_user_profile_not_found(self, api_client, all_perm_token):
        """
        User does not have a related profile
        """

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["birthday", "gender", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 200
        assert response_data["data"] == "No data found."
        assert response_data["message"] == "Completed."

    def test_user_did_not_set_fetch_fields(
        self, profile_record, api_client, user1_token, monkeypatch
    ):
        """
        User did not set the USER_PROFILE_FIELDS in settings .
        """
        monkeypatch.delitem(
            settings.ONE_TO_ONE_MODELS["demo_app.UserProfile"],
            "fetch_fields",
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        one_to_one_fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "fields": ["birthday", "gender", "primary_number"],
                }
            }
        }

        response = api_client.post(
            "/v1/1-1/",
            one_to_one_fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "fetch_fields must be configured."
        assert response_data["code"] == "DGA-S021"
