# Test cases for fetch API
import json
from unittest import mock

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from fixtures.API import (
    api_client,
    view_perm_token,
    add_perm_token,
    save_perm_user,
    view_perm_user,
    customer1,
    customer2,
)

# To ensure the import is retained
_ = save_perm_user


@pytest.mark.django_db
class TestGenericFetchAPI:

    def test_fetch_check_user_permission(
        self, customer1, api_client, view_perm_token
    ):
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
                            "operation": "or",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": False,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 1
        assert response_data["data"] == [
            {"name": customer1.name, "email": customer1.email}
        ]

    def test_fetch_filter_operator_eq(
        self, customer1, api_client, view_perm_token
    ):
        """
        Fetch operator is eq
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
                            "operation": "or",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 1
        assert response_data["data"] == [
            {"name": customer1.name, "email": customer1.email}
        ]

    def test_fetch_filter_operator_in(
        self, customer1, customer2, api_client, view_perm_token
    ):
        """
        Fetch operator is in
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "in",
                            "name": "phone_no",
                            "value": ["123456", "456789"],
                            "operation": "or",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 2
        assert response_data["data"] == [
            {"name": customer2.name, "email": customer2.email},
            {"name": customer1.name, "email": customer1.email},
        ]

    def test_fetch_filter_operator_not(
        self, customer2, api_client, view_perm_token
    ):
        """
        Fetch operator is not
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "not",
                            "name": "phone_no",
                            "value": ["123456"],
                            "operation": "or",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 1
        assert response_data["data"] == [
            {"name": customer2.name, "email": customer2.email},
        ]

    def test_fetch_filter_operator_gt(
        self, customer1, customer2, api_client, view_perm_token
    ):
        """
        Fetch operator is gt
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "gt",
                            "name": "phone_no",
                            "value": ["012"],
                            "operation": "or",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 2
        assert response_data["data"] == [
            {"name": customer2.name, "email": customer2.email},
            {"name": customer1.name, "email": customer1.email},
        ]

    def test_fetch_filter_operator_gt_2(
        self, customer1, customer2, api_client, view_perm_token
    ):
        """
        Fetch operator is gt
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "gt",
                            "name": "phone_no",
                            "value": ["999999"],
                            "operation": "or",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 0
        assert response_data["data"] == []

    def test_fetch_filter_operator_like(
        self, customer1, api_client, view_perm_token
    ):
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "like",
                            "name": "address",
                            "value": ["hyd"],
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["total"] == 1
        assert response_data["data"] == [
            {"name": "test_user1", "email": "user1@gmail.com"},
        ]

    def test_payload_missing_field_property(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has missed a required field in payload format
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required('fields',)"
        assert response_data["code"] == "DGA-V006"

    def test_fetch_access_denied(self, api_client):
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
        response = api_client.post("/fetch/", fetch_payload, format="json")
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Unauthorized access"
        assert response_data["code"] == "DGA-S001"

    def test_invalid_token_format(self, api_client, view_perm_token):
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Invalid Token"
        assert response_data["code"] == "DGA-S002"

    def test_invalid_payload_format(
        self, customer1, api_client, view_perm_token
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
            "/fetch/",
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

    def test_invalid_model_name(self, customer1, api_client, view_perm_token):
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 404
        assert response_data["error"] == ""
        assert response_data["code"] == "DGA-V007"

    def test_fetch_unauthorized(self, customer1, api_client, add_perm_token):
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
            "/fetch/",
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

    def test_invalid_model_name_non_string(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has given modelName not as string.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": 123,
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "Input should be a valid string('modelName',)"
        )
        assert response_data["code"] == "DGA-V006"

    def test_invalid_payload_fields_data_type(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has not given fields as list of strings
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": "name",
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"] == "Input should be a valid list('fields',)"
        )
        assert response_data["code"] == "DGA-V006"

    def test_unknown_fetch_filter_name(
        self, customer1, api_client, view_perm_token
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
                            "name": "ABC",
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V009"
        assert (
            response_data["error"]
            == "{'error': \"Extra field {'ABC'}\", 'code': 'DGA-U002'}"
        )

    def test_invalid_fetch_filter_format(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has given wrong format for fetch filters.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": ["phone_no", "eq", 123456],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        # Send a POST request to the fetch endpoint without authentication
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be a valid dictionary or instance of FetchFilter('filters', 0)"
        )

    def test_invalid_fetch_filter_operator(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has given invalid filter operator.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "ge",
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be 'eq', 'in', 'not', 'gt' or 'like'('filters', 0, "
            "'operator')"
        )

    def test_invalid_fetch_filter_name_datatype(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has given invalid datatype for filter name
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": 123456,
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be a valid string('filters', 0, 'name')"
        )

    def test_invalid_fetch_filter_value_element_datatype(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has given invalid filter operator.
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {"operator": "in", "name": "dob", "value": ["456789"]}
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V009"
        assert (
            response_data["error"]
            == "{'error': \"Invalid data: ['456789'] for dob\", 'code': 'DGA-S004'}"
        )

    def test_invalid_filter_value_length_for_eq_operator(
        self, customer1, api_client, view_perm_token
    ):
        """
        User has given invalid filter operator.
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
                            "value": ["123456", "456789"],
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
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Value error, Multiple filters not supported('filters',)"
        )

    def test_invalid_filters_operation(
        self, customer1, api_client, view_perm_token
    ):
        """
        Test the fetch endpoint with filters operation set to a value other
        than "or" or "and".
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
                            "operation": "not",
                        }
                    ],
                    "pageNumber": 1,
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be 'or' or 'and'('filters', 0, 'operation')"
        )

    def test_unknown_page_number(self, customer1, api_client, view_perm_token):
        """
        User does not send pagesize as int.
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
                    "pageNumber": "abc",
                    "pageSize": 10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be a valid integer, unable to parse string as an integer('pageNumber',)"
        )

    def test_negative_page_size(self, customer1, api_client, view_perm_token):
        """
        Test the fetch endpoint with pageNumber or pageSize set to a negative integer.
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
                    "pageSize": -10,
                    "sort": {"field": "name", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["code"] == "DGA-V009"
        assert response_data["error"] == "Negative indexing is not supported."

    def test_unknown_format_sort_property(
        self, customer1, api_client, view_perm_token
    ):
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
                    "sort": ["name", "desc"],
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be a valid dictionary or instance of FetchSort('sort',)"
        )

    def test_extra_keys_in_sort(self, customer1, api_client, view_perm_token):
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
                    "sort": {"field": "name", "order_by": "desc", "abc": 123},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Extra inputs are not permitted('sort', 'abc')"
        )

    def test_invalid_sort_field(self, customer1, api_client, view_perm_token):
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
                    "sort": {"field": "ABCD", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V009"
        assert (
            response_data["error"]
            == "{'error': \"Extra field {'ABCD'}\", 'code': 'DGA-U002'}"
        )

    def test_invalid_sort_order_by(
        self, customer1, api_client, view_perm_token
    ):
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
                    "sort": {"field": "name", "order_by": "and"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be 'asc' or 'desc'('sort', 'order_by')"
        )

    def test_invalid_distinct_value(
        self, customer1, api_client, view_perm_token
    ):
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
                    "distinct": 123,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be a valid boolean, unable to interpret input('distinct',)"
        )

    @mock.patch("rest_framework_simplejwt.tokens.AccessToken.verify")
    def test_expired_token_fetch(
        self, mock_verify, api_client, view_perm_user
    ):
        """
        User is using an expired token to fetch.
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
                    "distinct": True,
                }
            }
        }

        mock_verify.side_effect = Exception("Token is invalid or expired")

        token = AccessToken.for_user(view_perm_user)
        expired_access_token = str(token)

        headers = {"Authorization": f"Bearer {expired_access_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 401
        assert (
            response_data["error"]
            == "Authentication failed: Token is invalid or expired"
        )
        assert response_data["code"] == "DGA-S003"


@pytest.mark.parametrize(
    "fetch_payload, expected_status, expected_response",
    [
        # Positive Scenario
        (
            {
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
                        "distinct": True,
                    }
                }
            },
            200,
            {
                "total": 1,
                "data": [{"name": "test_user1", "email": "user1@gmail.com"}],
            },
        ),
        # Missing Required Field Scenario
        (
            {
                "payload": {
                    "variables": {
                        "modelName": "customer",
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
            },
            400,
            {
                "error": "Field required('fields',)",
                "code": "DGA-V006",
            },
        ),
    ],
)
@pytest.mark.django_db
class TestFetchScenarios:
    def test_fetch(
        self,
        customer1,
        fetch_payload,
        expected_status,
        expected_response,
        api_client,
        view_perm_token,
    ):
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == expected_status
        assert response_data == expected_response
