import pytest

from fixtures.api import (
    api_client,
    all_perm_token,
    all_perm_user,
    inactive_user_token,
    inactive_user,
)

usage = all_perm_user
usage1 = inactive_user


@pytest.mark.django_db
class TestUserInfoAPI:

    def test_user_info_success(self, api_client, all_perm_token):
        headers = {"Authorization": f"Bearer {all_perm_token}"}

        response = api_client.post(
            "/v1/user-info/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 200
        assert response_data["data"] == {
            "data": {
                "first_name": "test1",
                "last_name": "test2",
                "is_active": True,
            }
        }
        assert response_data["message"] == "Completed."

    def test_inactive_user_info(self, api_client, inactive_user_token):
        headers = {"Authorization": f"Bearer {inactive_user_token}"}

        response = api_client.post(
            "/v1/user-info/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "User is inactive"
        assert response_data["code"] == "DGA-U005"

    def test_user_null_header(self, api_client):
        response = api_client.post(
            "/v1/user-info/",
            format="json",
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "User not authenticated."
        assert response_data["code"] == "DGA-V037"

    def test_user_info_verbose_name(
        self, api_client, all_perm_token, monkeypatch
    ):
        """
        User sends a field with its verbose name.
        """
        monkeypatch.setattr(
            "django.conf.settings.USER_INFO_FIELDS",
            ("first name", "email"),
        )

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        response = api_client.post(
            "/v1/user-info/",
            format="json",
            headers=headers,
        )

        response_data = response.data
        assert response.status_code == 200
        assert response_data["data"] == {
            "data": {"email": "all_perm@test.com", "first_name": "test1"}
        }
        assert response_data["message"] == "Completed."

    def test_user_sends_unknown_field(
        self, api_client, all_perm_token, monkeypatch
    ):
        """
        User sends a not yet field in settings
        """
        monkeypatch.setattr(
            "django.conf.settings.USER_INFO_FIELDS",
            ("ABCD",),
        )

        headers = {"Authorization": f"Bearer {all_perm_token}"}

        response = api_client.post(
            "/v1/user-info/",
            format="json",
            headers=headers,
        )

        response_data = response.data

        assert response.status_code == 400
        assert response_data["error"] == "'[ABCD]'s not in the model."
        assert response_data["code"] == "DGA-U006"
