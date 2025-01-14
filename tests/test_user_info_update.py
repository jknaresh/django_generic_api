import json

import pytest

from fixtures.api import (
    api_client,
    all_perm_token,
    all_perm_user,
)

from django.contrib.auth.models import User

usage = all_perm_user


@pytest.mark.django_db
class TestUserInfoUpdateAPI:

    def test_user_info_update_success(self, api_client, all_perm_token):

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": {"first_name": "Fname", "last_name": "Lname"}
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 201
        assert response_data["data"] == [{"id": 1}]
        assert (
            response_data["message"]
            == "allpermuser@gmail.com's info is updated"
        )

        inserted_data = User.objects.get(id=1)
        assert inserted_data.first_name == "Fname"
        assert inserted_data.last_name == "Lname"

    def test_user_info_update_no_header(self, api_client):

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": {"first_name": "Fname", "last_name": "Lname"}
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "User not authenticated."
        assert response_data["code"] == "DGA-V031"

    def test_user_updates_unregistered_fields(
        self, api_client, all_perm_token
    ):

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": {
                        "first_name": "Fname",
                        "last_name": "Lname",
                        "extra_field": 123,
                    }
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Extra inputs are not permitted. ('extra_field',)\", 'code': 'DGA-S013'}"
        )
        assert response_data["code"] == "DGA-V033"

    def test_user_update_invalid_payload(self, api_client, all_perm_token):

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "ABC": 123,
                    "saveInput": {
                        "first_name": "Fname",
                        "last_name": "Lname",
                        "extra_field": 123,
                    },
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V032"

    def test_user_update_invalid_element_datatype(
        self, api_client, all_perm_token
    ):

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": {
                        "first_name": "Fname",
                        "last_name": False,
                    },
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Input should be a valid string. ('last_name',)\", 'code': 'DGA-S013'}"
        )
        assert response_data["code"] == "DGA-V033"

    def test_user_active_boolean_field_set_false_update(
        self, api_client, all_perm_token
    ):

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": {
                        "first_name": "Fname",
                        "last_name": "Lname",
                        "is_active": False,
                    }
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert response_data["data"] == [{"id": 1}]
        assert (
            response_data["message"]
            == "allpermuser@gmail.com's info is updated"
        )

        inserted_data = User.objects.get(id=1)
        assert inserted_data.is_active == False

    def test_unknown_field_in_settings_variable(
        self, api_client, all_perm_token, monkeypatch
    ):

        monkeypatch.setattr(
            "django.conf.settings.USER_INFO_FIELDS",
            ("first_name", "last_name", "not_yet_field"),
        )

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        user_info_update_payload = {
            "payload": {
                "variables": {
                    "saveInput": {"first_name": "Fname", "last_name": "Lname"}
                }
            }
        }

        response = api_client.put(
            "/user-info/",
            user_info_update_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "'[not_yet_field]'s not in the model."
        assert response_data["code"] == "DGA-V033"
