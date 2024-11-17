# Test cases for fetch API
import pytest
from rest_framework.test import APIClient
from api_app.models import Customer
import json
from test_support import (
    api_client,
    fetch_data_1,
    view_perm_token,
    add_perm_token,
    view_perm_user,
    save_perm_user,
)
from unittest import mock
from rest_framework_simplejwt.tokens import AccessToken


@pytest.mark.django_db
class TestGenericFetchAPI:

    def test_missing_required_field(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required('fields',)"
        assert response_data["code"] == "DGA-V006"

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

    def test_modelName_not_str(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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

    def test_wrong_fields_datatype(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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

    def test_invalid_fetch_filter_field(
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
            == "{'error': \"Extra field {'ABC'}\", 'code': 'DGA-U002'}"
        )

    def test_invalid_fetch_filter_format(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["code"] == "DGA-V006"
        assert (
            response_data["error"]
            == "Input should be 'eq', 'in', 'not' or 'gt'('filters', 0, 'operator')"
        )

    def test_invalid_fetch_filter_name_datatype(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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

    def test_invalid_fetch_filter_name_field(
        self, fetch_data_1, api_client, view_perm_token
    ):
        """
        User has given invalid field for filters.name
        """
        fetch_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
                    "fields": ["name", "email"],
                    "filters": [
                        {
                            "operator": "eq",
                            "name": "ABCD",
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
        assert response_data["code"] == "DGA-V009"
        assert (
            response_data["error"]
            == "{'error': \"Extra field {'ABCD'}\", 'code': 'DGA-U002'}"
        )

    def test_invalid_fetch_filter_value_datatype(
        self, fetch_data_1, api_client, view_perm_token
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
            == "{'error': \"Invalid data: ['456789'] for dob\", 'code': 'DGA-S004'}"
        )

    def test_multiple_filter_eq_operator(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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

    def test_pagesize_is_not_int(
        self, fetch_data_1, api_client, view_perm_token
    ):
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
            "/api/fetch/",
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

    def test_negative_page_size(
        self, fetch_data_1, api_client, view_perm_token
    ):
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
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["code"] == "DGA-V009"
        assert response_data["error"] == "Negative indexing is not supported."

    def test_sort_not_dictionary(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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

    def test_extra_keys_in_sort(
        self, fetch_data_1, api_client, view_perm_token
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
                    "sort": {"field": "name", "order_by": "desc", "abc": 123},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
        response = api_client.post(
            "/api/fetch/",
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

    def test_invalid_sort_field(
        self, fetch_data_1, api_client, view_perm_token
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
                    "sort": {"field": "ABCD", "order_by": "desc"},
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}
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
            == "{'error': \"Extra field {'ABCD'}\", 'code': 'DGA-U002'}"
        )

    def test_invalid_sort_order_by(
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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
        self, fetch_data_1, api_client, view_perm_token
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
            "/api/fetch/",
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

    def test_missing_authentication_header(self, fetch_data_1, api_client):
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
        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["code"] == "DGA-S001"
        assert response_data["error"] == "Unauthorized access"

    def test_incorrect_token_format(
        self, fetch_data_1, api_client, view_perm_token
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
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"ABCD {view_perm_token}"}

        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["code"] == "DGA-S002"
        assert response_data["error"] == "Invalid Token"

    def test_missing_view_permissions(
        self, fetch_data_1, api_client, add_perm_token
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
                    "distinct": True,
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
        assert response_data["code"] == "DGA-V008"
        assert (
            response_data["error"]
            == "Something went wrong!!! Please contact the administrator."
        )

    def test_positive_fetch_scenario(
        self, fetch_data_1, api_client, view_perm_token
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
                    "distinct": True,
                }
            }
        }
        headers = {"Authorization": f"Bearer {view_perm_token}"}

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
            "/api/fetch/",
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
        fetch_data_1,
        fetch_payload,
        expected_status,
        expected_response,
        api_client,
        view_perm_token,
    ):
        headers = {"Authorization": f"Bearer {view_perm_token}"}

        response = api_client.post(
            "/api/fetch/",
            fetch_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == expected_status
        assert response_data == expected_response
