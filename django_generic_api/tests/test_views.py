import pytest
from rest_framework.test import APIClient
from api_app.models import Customer
from model_bakery import baker
import json
from test_support import (
    all_perm_user,
    save_perm_user,
    view_perm_user,
    add_perm_token,
    view_perm_token,
    no_perm_token,
    fetch_data_1,
    api_client,
    login_user,
    email_activate_inactive_user_id,
)
from urllib.parse import quote
import time
from django.contrib.auth.models import User
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


@pytest.mark.django_db
class TestGenericSaveAPI:

    def test_missing_required_fields(self, api_client, add_perm_token):
        """
        Test the fetch endpoint with a payload that omits any of (modelName, saveInput).
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V002"

    def test_model_name_not_string(self, api_client, add_perm_token):
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Input should be a valid string"
        assert response_data["code"] == "DGA-V002"

    def test_model_name_not_exist(self, api_client, add_perm_token):
        """
        Test the fetch endpoint with modelName which does not exist.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "abcd",
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

    def test_save_input_length_greater_than_10(
        self, api_client, add_perm_token
    ):
        """
        Test the fetch endpoint with a length of saveInput greater than 10.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Only 10 records at once."
        assert response_data["code"] == "DGA-V001"

    def test_save_input_multiple_records(self, api_client, add_perm_token):
        """
        Test the save endpoint with multiple records in the saveInput array, where only one record should be updated at a time.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "customer",
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': 'Only 1 record to update at once', 'code': 'DGA-S005'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_user_passes_non_existent_field_in_save_input(
        self, api_client, add_perm_token
    ):
        """
        User passes a non-existent field in saveInput.
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
                            "ABC": "abcdef",
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
            == "{'error': \"Extra field {'ABC'}\", 'code': 'DGA-S009'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_user_passes_invalid_datatype_value(
        self, api_client, add_perm_token
    ):
        """
        User passes invalid datatype value to save into a field.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': ValidationError(['“01Jan2003” value has an invalid date format. It must be in YYYY-MM-DD format.']), 'code': 'DGA-S010'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_user_does_not_pass_required_field(
        self, api_client, add_perm_token
    ):
        """
        User does not pass a required field.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': 'NOT NULL constraint failed: api_app_customer.dob', 'code': 'DGA-S008'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_user_tries_to_update_non_existent_record(
        self, api_client, add_perm_token
    ):
        """
        User tries to update a record which does not exist.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': 'Record with (ID) 9000 does not exist', 'code': 'DGA-S007'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_user_tries_to_update_with_string_id(
        self, api_client, add_perm_token
    ):
        """
        User tries to update a record with string as ID.
        """
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert (
            response_data["error"]
            == "{'error': \"Field 'id' expected a number but got 'abc'.\", 'code': 'DGA-S008'}"
        )
        assert response_data["code"] == "DGA-V005"

    def test_authentication_header_not_passed(
        self, api_client, add_perm_token
    ):
        """
        User is not passing the authentication header.
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
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }

        response = api_client.post(
            "/api/save/",
            save_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 401
        assert response_data["error"] == "Unauthorized access"
        assert response_data["code"] == "DGA-S001"

    def test_invalid_token_format(self, api_client, add_perm_token):
        """
        User sends request with wrong token format.
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
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }
        headers = {"Authorization": f"ABCD {add_perm_token}"}
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

    def test_create_record_success(self, api_client, add_perm_token):
        """
        User has sent correct payload format.
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
            "/api/save/",
            save_payload,
            format="json",
            headers=headers,
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert response_data["data"] == [{"id": [1]}]
        assert response_data["message"] == ["Record created successfully."]

    def test_save_without_permission(self, api_client, view_perm_token):
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

    @mock.patch("rest_framework_simplejwt.tokens.AccessToken.verify")
    def test_expired_token_save(self, mock_verify, api_client, save_perm_user):
        """
        User is using an expired token to fetch.
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
                            "inserted_timestamp": "2024-11-10 11:11:11",
                            "status": "123",
                        }
                    ],
                }
            }
        }

        mock_verify.side_effect = Exception("Token is invalid or expired")

        token = AccessToken.for_user(save_perm_user)
        expired_access_token = str(token)

        headers = {"Authorization": f"Bearer {expired_access_token}"}

        response = api_client.post(
            "/api/save/",
            save_payload,
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

    def test_update_success_scenario(
        self, api_client, add_perm_token, fetch_data_1
    ):
        """
        This is a success update scenario.
        """
        data_id = fetch_data_1.id
        save_payload = {
            "payload": {
                "variables": {
                    "modelName": "Customer",
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
            "/api/save/",
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


@pytest.mark.django_db
class TestLoginAPI:

    def test_login_success(self, api_client, login_user):
        """
        This is a success scenario for user login .
        """
        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "123456"}
            }
        }

        # Sending POST request to login endpoint
        response = api_client.post("/api/login/", login_payload, format="json")
        response_data = json.loads(response.content.decode("utf-8"))

        # Assertions
        assert response.status_code == 200
        assert "refresh" in response_data["data"][0]
        assert "access" in response_data["data"][0]

    def test_missing_field_in_payload(self, api_client):
        """
        User has not passed a required field in payload.
        """
        login_payload = {
            "payload": {
                "variables": {
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
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V010"

    def test_extra_field_in_payload_format(self, api_client):
        """
        User has given an extra field in payload format.
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

    def test_login_by_session(self, api_client, login_user):
        """
        User hits the login API by using session.
        """
        login_payload = {
            "payload": {
                "variables": {"email": "user@gmail.com", "password": "123456"}
            }
        }

        headers = {"X-Requested-With": "XMLHttpRequest"}
        response = api_client.post(
            "/api/login/", login_payload, format="json", headers=headers
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Token generation not allowed."
        assert response_data["code"] == "DGA-V021"

    def test_login_credentials_invalid_datatype(self, api_client):
        """
        User sends credentials with wrong data type.
        """
        login_payload = {
            "payload": {"variables": {"email": 123465, "password": "123456"}}
        }
        response = api_client.post(
            "/api/login/",
            login_payload,
            format="json",
        )
        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "Input should be a valid string"
        assert response_data["code"] == "DGA-V010"


@pytest.mark.django_db
class TestAccountActivateAPI:

    def test_expired_activation_link(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User's activation link is expired.
        """
        timestamp = int(time.time()) - (25 * 60 * 60)  # 25 hours old timestamp
        token = f"{email_activate_inactive_user_id}:{timestamp}"

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))

        assert response.status_code == 400
        assert response_data["error"] == "The activation link has expired."
        assert response_data["code"] == "DGA-V018"

    def test_email_is_already_active(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User is already active.
        """

        user = User.objects.get(id=email_activate_inactive_user_id)
        user.is_active = True
        user.save()

        timestamp = int(time.time())
        token = f"{user.id}:{timestamp}"

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["message"] == "Account is already active."

    def test_user_does_not_exist(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User id does not exist
        """
        user = User.objects.get(id=email_activate_inactive_user_id)

        timestamp = int(time.time())
        token = f"{user.id}:{timestamp}"
        user.delete()

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 400
        assert response_data["error"] == "User not found."
        assert response_data["code"] == "DGA-V019"

    def test_user_activated_success(
        self, api_client, email_activate_inactive_user_id
    ):
        """
        User account is activated successfully.
        """
        timestamp = int(time.time())
        token = f"{email_activate_inactive_user_id}:{timestamp}"

        response = api_client.get(
            f"/api/activate/{token}/",
            format="json",
        )

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 201
        assert (
            response_data["message"]
            == "Your account has been activated successfully."
        )


@pytest.mark.django_db
class TestRegisterAPI:

    def test_missing_required_field(self, api_client):
        """
        User has not included a required field in payload.
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "ab@gmail.com",
                    "password": "123456",
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
        assert response_data["error"] == "Field required"
        assert response_data["code"] == "DGA-V013"

    def test_extra_field_in_payload(self, api_client):
        """
        User's Register payload consists an extra field.
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

    def test_registration_success(self, api_client):
        """
        User registration is success.
        """
        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@gmail.com",
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

        timestamp = int(time.time())
        token = f"{1}:{timestamp}"
        final = quote(token)
        link = f"http://127.0.0.1:8050/api/activate/{final}/"

        response_data = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 200
        assert response_data["message"] == f"Email sent successfully. {link}"

    def test_invalid_domain(self, api_client):
        """
        User has registered with an invalid domain
        """

        register_payload = {
            "payload": {
                "variables": {
                    "email": "abc@abcdef.com",
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
        assert response_data["error"] == "Invalid email domain"
        assert response_data["code"] == "DGA-V022"

    def test_email_already_exist(self, api_client, login_user):
        """
        User registers with an existing email.
        """

        register_payload = {
            "payload": {
                "variables": {
                    "email": "user@gmail.com",
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
        assert (
            response_data["error"] == "Account already exists with this email."
        )
        assert response_data["code"] == "DGA-V015"
