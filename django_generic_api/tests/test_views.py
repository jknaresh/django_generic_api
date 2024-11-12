import pytest
from rest_framework.test import APIClient, RequestsClient
from api_app.models import Customer
from model_bakery import baker
import json
from test_support import (
    all_perm_user,
    save_perm_user,
    view_perm_user,
    all_perm_token,
    add_perm_token,
    view_perm_token,
    no_perm_token,
    fetch_data_1,
    api_client,
    login_user,
    inactive_user_wrong_token,
)
import pdb
import datetime


@pytest.mark.django_db
class TestGenericFetchAPI:

    def test_fetch_not_authenticated(self, api_client):
        """
        User fetches without Authentication Header
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "phone_no",
                            "value": ["456789"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post("/api/fetch/", fetch_payload, format="json")
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Unauthorized access"
        assert response_data["code"] == "DGA-S001"

    def test_wrong_token_format(self, api_client, view_perm_token):
        """
        Token format is wrong.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "phone_no",
                            "value": ["123456"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"ABCD {view_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Invalid Token"
        assert response_data["code"] == "DGA-S002"

    def test_fetch_perm_user(self, fetch_data_1, api_client, view_perm_token):
        """
        User has view permissions.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "phone_no",
                            "value": ["123456"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 1
        assert response_data["data"] == [
            {"name": "test_user1", "email": "user1@gmail.com"}
        ]

    def test_wrong_payload_format(
        self, fetch_data_1, api_client, view_perm_token
    ):
        """
        User has given wrong format in payload
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "extra_field": "ABC",
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "phone_no",
                            "value": ["123456"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "Extra inputs are not permitted('extra_field',)"
        )
        assert response_data["code"] == "DGA-V006"

    def test_invalid_model_name(
        self, fetch_data_1, api_client, view_perm_token
    ):
        """
        User has given invalid model name.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "ABC123",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "phone_no",
                            "value": ["123456"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert response_data["error"] == ""
        assert response_data["code"] == "DGA-V007"

    def test_no_fetch_perm(self, fetch_data_1, api_client, add_perm_token):
        """
        User does not have view permissions.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "phone_no",
                            "value": ["123456"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert (
            response_data["error"]
            == "Something went wrong!!! Please contact the administrator."
        )
        assert response_data["code"] == "DGA-V008"

    def test_invalid_fetch_filter_value_1(
        self, fetch_data_1, api_client, view_perm_token
    ):
        """
        User has given invalid fetch data.
        address accepts str, given int
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "address",
                            "value": [123456],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V009"
        assert (
            response_data["error"]
            == "{'error': 'Invalid data: [123456]', 'code': 'DGA-S004'}"
        )


@pytest.mark.django_db
class TestGenericSaveAPI:

    def test_save_not_authenticated(self, api_client):
        """
        User fetches without Authentication Header
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "name04",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10",
                            "status": "123",
                        }
                    ],
                }
            }
        }

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post("/api/save/", save_payload, format="json")
        assert response.status_code == 401
        response_data = json.loads(response.content.decode("utf-8"))
        assert "error" in response_data
        assert response_data["error"] == "Unauthorized access"
        assert "code" in response_data
        assert response_data["code"] == "DGA-S001"

    def test_wrong_token_format(self, api_client, add_perm_token):
        """
        Token format is wrong.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "name04",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"ABCD {add_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Invalid Token"
        assert response_data["code"] == "DGA-S002"

    def test_add_perm_user(self, api_client, add_perm_token):
        """
        User has view permissions.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert response_data["data"] == [{"id": [1]}]
        assert response_data["message"] == ["Record created successfully."]

    def test_save_10plus_records(self, api_client, add_perm_token):
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user2",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user3",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user4",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user5",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user6",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user7",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user8",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user9",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user10",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user11",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user12",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user13",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Only 10 records at once."
        assert response_data["code"] == "DGA-V001"

    def test_wrong_payload_format(self, api_client, add_perm_token):
        """
        User has given wrong payload format.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "invalid_field": "ABC",
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V002"

    def test_invalid_model_name(self, api_client, add_perm_token):
        """
        User has given invalid model name
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "ABC123",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Model not found"
        assert response_data["code"] == "DGA-V003"

    def test_no_save_perm(self, api_client, view_perm_token):
        """
        User does not have save permission.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert (
            response_data["error"]
            == "Something went wrong!!! Please contact the administrator."
        )
        assert response_data["code"] == "DGA-V004"

    def test_invalid_saveInput_1(self, api_client, add_perm_token):
        """
        User has given wrong payload format.
        inserted_timestamp(null=False is given as null)
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": None,
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Input should be a valid string. ('inserted_timestamp',)\", 'code': 'DGA-S006'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_invalid_saveInput_2(self, api_client, add_perm_token):
        """
        User has given wrong payload format.
        address(str) is given as int
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": 123,
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Input should be a valid string. ('address',)\", 'code': 'DGA-S006'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_user_updates_multiple_records(self,api_client,add_perm_token):
        """
        User tries updating multiple records at once.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": 1,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user2",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user3",
                            "dob": "2024-11-04",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ]
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] ==  "{'error': 'Only 1 record to update at once', 'code': 'DGA-S005'}"
        assert response_data["code"] == "DGA-V005"

    def test_invalid_saveInput_3(self,api_client,add_perm_token):
        """
        User passes wrong model configuration in payload.
        """


@pytest.mark.django_db
class TestLoginAPI:

    def test_wrong_payload_format(self, api_client):
        """
        user has given wrong payload format
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


@pytest.mark.django_db
class TestRegisterAPI:

    def test_wrong_payload_format(self, api_client):
        """
        User's Register payload does not match predefined payload
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "extra_field": "ABCD",
                    "password": "123456",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Extra inputs are not permitted"
        assert response_data["code"] == "DGA-V013"

    def test_passwords_dont_match(self, api_client):
        """
        User's Register payload does not match predefined payload
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "password": "123456789",
                    "password1": "123456",
                }
            }
        }

        response = api_client.post(
            "/api/register/",
            register_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "passwords does not match"
        assert response_data["code"] == "DGA-V014"

    # todo: update txt file finding method
    # def test_user_already_exists(self,api_client,login_user):
    #     """
    #     User already exists.
    #     """
    #     register_payload = {
    #         "payload": {
    #             "variables": {
    #                 "email": "user@gmail.com",
    #                 "password": "123456",
    #                 "password1": "123456"
    #             }
    #         }
    #     }
    #
    #     response = api_client.post(
    #         "/api/register/",
    #         register_payload,
    #         format="json",
    #     )
    #     response_data = json.loads(response.content.decode("utf-8"))
    #     assert response.status_code == 400
    #     assert response_data["error"] == "Account already exists with this email."
    #     assert response_data["code"] == "DGA-V015"
