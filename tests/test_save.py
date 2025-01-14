import json
from unittest.mock import patch

import pytest
from django_generic_api.tests.demo_app.models import Customer
from rest_framework_simplejwt.exceptions import TokenError

from fixtures.api import (
    save_perm_user,
    view_perm_user,
    add_perm_token,
    view_perm_token,
    api_client,
    customer1,
)

# To ensure the import is retained
usage = view_perm_user
usage1 = save_perm_user


@pytest.mark.django_db
class TestGenericSaveAPI:

    def test_create_record_with_appname(self, api_client, add_perm_token):
        """
        User has sent correct payload format.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}
        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert response_data["data"] == [{"id": [1]}]
        assert response_data["message"] == ["Record created successfully."]

    def test_create_record_without_appname(self, api_client, add_perm_token):
        """
        User's payload does not consist appname.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}
        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert response_data["data"] == [{"id": [1]}]
        assert response_data["message"] == ["Record created successfully."]

    def test_update_record(self, api_client, add_perm_token, customer1):
        """
        This is a success update scenario.
        """
        data_id = customer1.id

        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": data_id,
                    "saveInput": [
                        {
                            "name": "ABCD",
                            "dob": "2020-01-21",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}
        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 201
        assert response_data["data"] == [{"id": [data_id]}]
        assert response_data["message"] == ["Record updated successfully."]

        updated_data = Customer.objects.get(id=data_id)
        assert updated_data.name == "ABCD"

    def test_create_record_with_incorrect_appname(
        self, api_client, add_perm_token
    ):
        """
        User has sent correct payload format.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app1.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}
        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Model not found"
        assert response_data["code"] == "DGA-V003"

    def test_create_record_with_incorrect_model_name(
        self, api_client, add_perm_token
    ):
        """
        User has sent correct payload format.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer1",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}
        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Model not found"
        assert response_data["code"] == "DGA-V003"

    def test_invalid_payload_format(self, api_client, add_perm_token):
        """
        Test the fetch endpoint with a payload that omits any of (modelName,
        saveInput).
        """
        save_payload = {
            "payload": {
                "variables": {
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V002"

    def test_invalid_model_name_non_string(self, api_client, add_perm_token):
        """
        Test the fetch endpoint with modelName not as a string.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": 123,
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Input should be a valid string"
        assert response_data["code"] == "DGA-V002"

    def test_invalid_model_name(self, api_client, add_perm_token):
        """
        Test the fetch endpoint with modelName which does not exist.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.abcd",
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Model not found"
        assert response_data["code"] == "DGA-V003"

    def test_save_input_length_greater_than_10(
        self, api_client, add_perm_token
    ):
        """
        Test the fetch endpoint with a length of saveInput greater than 10.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.customer",
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
                            "email": "ltest2@mail.com",
                            "phone_no": "012346",
                            "address": "HYD",
                            "pin_code": "101",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user3",
                            "dob": "2024-11-04",
                            "email": "ltest3@mail.com",
                            "phone_no": "012347",
                            "address": "HYD",
                            "pin_code": "102",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user4",
                            "dob": "2024-11-04",
                            "email": "ltest4@mail.com",
                            "phone_no": "012348",
                            "address": "HYD",
                            "pin_code": "103",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user5",
                            "dob": "2024-11-04",
                            "email": "ltest5@mail.com",
                            "phone_no": "012349",
                            "address": "HYD",
                            "pin_code": "104",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user6",
                            "dob": "2024-11-04",
                            "email": "ltest6@mail.com",
                            "phone_no": "012350",
                            "address": "HYD",
                            "pin_code": "105",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user7",
                            "dob": "2024-11-04",
                            "email": "ltest7@mail.com",
                            "phone_no": "012351",
                            "address": "HYD",
                            "pin_code": "106",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user8",
                            "dob": "2024-11-04",
                            "email": "ltest8@mail.com",
                            "phone_no": "012352",
                            "address": "HYD",
                            "pin_code": "107",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user9",
                            "dob": "2024-11-04",
                            "email": "ltest9@mail.com",
                            "phone_no": "012353",
                            "address": "HYD",
                            "pin_code": "108",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user10",
                            "dob": "2024-11-04",
                            "email": "ltest10@mail.com",
                            "phone_no": "012354",
                            "address": "HYD",
                            "pin_code": "109",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                        {
                            "name": "test_user11",
                            "dob": "2024-11-04",
                            "email": "ltest11@mail.com",
                            "phone_no": "012355",
                            "address": "HYD",
                            "pin_code": "110",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        },
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Only 10 records at once."
        assert response_data["code"] == "DGA-V001"

    def test_update_multiple_records(self, api_client, add_perm_token):
        """
        Test the save endpoint with multiple records in the saveInput array,
        where only one record should be updated at a time.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.customer",
                    "id": 10,
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
                            "name": "test_user1",
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': 'Only 1 record to update at once', 'code': "
            "'DGA-S005'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_unknown_save_input_field(self, api_client, add_perm_token):
        """
        User passes a non-existent field in saveInput.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
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
                            "ABC": "abcdef",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}

        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Extra inputs are not permitted. ('ABC',)\", 'code': 'DGA-S006'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_invalid_save_input_element_datatype(
        self, api_client, add_perm_token
    ):
        """
        User passes invalid datatype value to save into a field.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "01Jan2003",  # Invalid date format
                            "email": "ltest1@mail.com",
                            "phone_no": "789465",
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Input should be a valid date or datetime, input is too short. ('dob',)\", 'code': 'DGA-S006'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_missing_required_field_save_input(
        self, api_client, add_perm_token
    ):
        """
        User does not pass a required field.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            # dob is not passed which is a required field
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"] == "{'error': 'NOT NULL constraint failed: "
            "demo_app_customer.dob', 'code': 'DGA-S008'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_update_unknown_record(self, api_client, add_perm_token):
        """
        User tries to update a record which does not exist.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": 9000,  # ID that does not exist
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': 'Record with (ID) 9000 does not exist', "
            "'code': 'DGA-S007'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_invalid_id_element_datatype(self, api_client, add_perm_token):
        """
        User tries to update a record with string as ID.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": "abc",  # String as ID
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Field 'id' expected a number but got "
            "'abc'.\", 'code': 'DGA-S008'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_save_access_denied(self, api_client, add_perm_token):
        """
        User is not passing the authentication header.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
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

        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert (
            response_data["error"]
            == "Something went wrong!!! Please contact the administrator."
        )
        assert response_data["code"] == "DGA-V004"

    def test_invalid_token_format(self, api_client, add_perm_token):
        """
        User sends request with wrong token format.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
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
        headers = {"Authorization": f"ABCD {add_perm_token}"}
        response = api_client.post(
            "/save/",
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

    def test_save_unauthorized(self, api_client, view_perm_token):
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
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
            "/save/",
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

    def test_user_active_boolean_field_set_false(
        self, api_client, add_perm_token
    ):
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
                            "email": "ltest1@mail.com",
                            "phone_no": "012345",
                            "address": "HYD",
                            "pin_code": "100",
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                            "is_alive": False,
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"Bearer {add_perm_token}"}
        response = api_client.post(
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert response_data["data"] == [{"id": [1]}]
        assert response_data["message"] == ["Record created successfully."]

        inserted_data = Customer.objects.get(id=1)
        assert inserted_data.is_alive == False

    @patch("rest_framework_simplejwt.tokens.AccessToken.verify")
    def test_expired_token_save(self, mock_verify, api_client, add_perm_token):
        """
        User is using an expired token to save.
        """
        # Configure mock to raise TokenError to simulate expired token
        mock_verify.side_effect = TokenError("Token is invalid or expired")

        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "demo_app.Customer",
                    "id": None,
                    "saveInput": [
                        {
                            "name": "test_user1",
                            "dob": "2020-01-21",
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
            "/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 401
        assert response_data["error"] == "Invalid Token."
        assert response_data["code"] == "DGA-U004"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload, expected_status, expected_error, expected_code, "
    "expected_message, expected_data",
    [
        # Test missing required fields (modelName is missing)
        (
            {
                "payload": {
                    "variables": {
                        "id": None,
                        "saveInput": [
                            {
                                "name": "test_user1",
                                "dob": "2024-11-04",
                                "email": "ltest1@mail.com",
                                "phone_no": "012345",
                                "address": "HYD",
                                "pin_code": "100",
                                "inserted_timestamp": "2024-11-10 " "11:11:11",
                                "status": "123",
                            }
                        ],
                    }
                }
            },
            400,
            "Field required",
            "DGA-V002",
            None,
            None,
        ),
        # Test creating a record successfully
        (
            {
                "payload": {
                    "variables": {
                        "modelName": "demo_app.Customer",
                        "id": None,
                        "saveInput": [
                            {
                                "name": "test_user1",
                                "dob": "2020-01-21",
                                "email": "ltest1@mail.com",
                                "phone_no": "012345",
                                "address": "HYD",
                                "pin_code": "100",
                                "status": "123",
                            }
                        ],
                    }
                }
            },
            201,
            None,
            None,
            ["Record created successfully."],
            [{"id": [1]}],
        ),
    ],
)
def test_save_api(
    api_client,
    add_perm_token,
    payload,
    expected_status,
    expected_error,
    expected_code,
    expected_message,
    expected_data,
):
    headers = {"Authorization": f"Bearer {add_perm_token}"}

    response = api_client.post(
        "/save/",
        payload,
        format="json",
        headers=headers,
    )
    response_data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == expected_status

    if expected_error:
        assert response_data["error"] == expected_error
        assert response_data["code"] == expected_code
    if expected_message:
        assert response_data["message"] == expected_message
    if expected_data:
        assert response_data["data"] == expected_data
