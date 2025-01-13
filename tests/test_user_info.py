import json

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
            "/user-info/",
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 200
        assert response_data["data"][0]["email"] == "all_perm@test.com"
        assert response_data["data"][0]["first_name"] == "test1"
        assert response_data["data"][0]["last_name"] == "test2"

    def test_inactive_user_info(self, api_client, inactive_user_token):

        headers = {"Authorization": f"Bearer {inactive_user_token}"}

        response = api_client.post(
            "/user-info/",
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "User is inactive"
        assert response_data["code"] == "DGA-U005"

    def test_user_null_header(self, api_client):

        response = api_client.post(
            "/user-info/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "User not authenticated."
        assert response_data["code"] == "DGA-V030"
