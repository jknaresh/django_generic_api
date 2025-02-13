from datetime import date

import pytest
from django.conf import settings
from django_generic_api.tests.demo_app.models import UserProfile
from django.db import IntegrityError
from fixtures.api import (
    api_client,
    user1_token,
    user1,
    profile_record,
    all_perm_token,
    all_perm_user,
)
from unittest import mock

usage = user1
usage1 = all_perm_user


@pytest.mark.django_db
class TestUserProfileUpdateAPI:

    def test_user_profile_create_success(self, api_client, all_perm_token):
        """
        A profile is created for user successfully.
        """
        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "gender": "M",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data
        inserted_data = UserProfile.objects.get(id=1)
        assert response.status_code == 201
        assert response_data["data"] == [{"id": 1}]
        assert (
            response_data["message"]
            == "allpermuser@gmail.com's profile is created"
        )

        assert inserted_data.birthday == date.fromisoformat("2025-01-01")
        assert inserted_data.gender == "M"
        assert inserted_data.primary_number == "123456"

    def test_user_profile_update_success(
        self, api_client, profile_record, user1_token
    ):
        """
        User has successfully updated the user profile.
        """
        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "gender": "M",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data
        inserted_data = UserProfile.objects.get(id=1)

        assert response.status_code == 200
        assert response_data["data"] == [{"id": 1}]
        assert response_data["message"] == "user@test.com's profile is updated"

        assert inserted_data.birthday == date.fromisoformat("2025-01-01")
        assert inserted_data.gender == "M"
        assert inserted_data.primary_number == "123456"

    def test_user_does_not_pass_header(self, api_client):
        """
        User does not pass any header for authentication
        """

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "gender": "M",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "User not authenticated."
        assert response_data["code"] == "DGA-V044"

    def test_user_passes_wrong_payload_format(self, api_client, user1_token):
        """
        User's payload format is invalid.
        """
        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "gender": "M",
                            "primary_number": "123456",
                        }
                    ]
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V046"

    def test_no_profile_model_settings(
        self, api_client, user1_token, monkeypatch
    ):
        """
        User does not configure ONE_TO_ONE_MODELS in settings
        """
        if hasattr(settings, "ONE_TO_ONE_MODELS"):
            monkeypatch.delattr(settings, "ONE_TO_ONE_MODELS")

        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "gender": "M",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data
        assert response.status_code == 400
        assert (
            response_data["error"] == "Set settings for User Related models."
        )
        assert response_data["code"] == "DGA-S019"

    def test_profile_model_not_found(
        self, api_client, user1_token, monkeypatch
    ):
        """
        User passes invalid profile model.
        """

        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.ABCD",
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "address": "HYDERABAD",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["error"] == "demo_app.ABCD is not configured."
        assert response_data["code"] == "DGA-S020"

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

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "fav_book": 10,
                            "address": "HYDERABAD",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert (
            response_data["error"] == "demo_app.UserProfile is not configured."
        )
        assert response_data["code"] == "DGA-S020"

    def test_no_profile_field_settings(
        self, api_client, user1_token, monkeypatch
    ):
        """
        User does not configure USER_PROFILE_MODEL in settings
        """
        monkeypatch.delitem(
            settings.ONE_TO_ONE_MODELS["demo_app.UserProfile"],
            "save_fields",
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "2025-01-01",
                            "address": "HYDERABAD",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data
        assert response.status_code == 400
        assert response_data["error"] == "save_fields must be configured."
        assert response_data["code"] == "DGA-S021"

    def test_invalid_data(self, api_client, user1_token):
        """
        User passes invalid data to save.
        """

        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "abcd",
                            "address": "HYDERABAD",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "Input should be a valid date or datetime, input is too short. ('birthday',)"
        )
        assert response_data["code"] == "DGA-S017"

    def test_invalid_fk_field_value(
        self, api_client, user1_token, monkeypatch
    ):
        """
        User sends not yet id for fk value.
        """

        monkeypatch.setitem(
            settings.ONE_TO_ONE_MODELS["demo_app.UserProfile"],
            "save_fields",
            (
                "fav_book",
                "address",
                "primary_number",
            ),
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "fav_book": 10,
                            "address": "HYDERABAD",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        with mock.patch(
            "django_generic_api.tests.demo_app.models.UserProfile.save",
            side_effect=IntegrityError,
        ):
            response = api_client.put(
                "/v1/1-1/",
                user_profile_update_payload,
                format="json",
                headers=headers,
            )

            response_data = response.data
            assert response.status_code == 400
            assert response_data["error"] == "Invalid foreign key constraint"
            assert response_data["code"] == "DGA-S022"

    def test_unknown_fields_are_configured(
        self, api_client, user1_token, monkeypatch
    ):
        """
        Unknown fields are configured in settings.
        :param api_client:
        :return:
        """
        monkeypatch.setitem(
            settings.ONE_TO_ONE_MODELS["demo_app.UserProfile"],
            "save_fields",
            ("ABCD",),
        )

        headers = {"Authorization": f"Bearer {user1_token}"}

        user_profile_update_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.UserProfile",
                    "saveInput": [
                        {
                            "birthday": "2024-10-10",
                            "address": "HYDERABAD",
                            "primary_number": "123456",
                        }
                    ],
                }
            }
        }

        response = api_client.put(
            "/v1/1-1/",
            user_profile_update_payload,
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "'[ABCD]'s not in the model."
        assert response_data["code"] == "DGA-U006"
