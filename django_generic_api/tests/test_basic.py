import pytest
from django_generic_api.tests.fixtures import sample_string, sample_dict
from django_generic_api.tests.demo_app.models import Customer
from model_bakery import baker


def test_sample_string(sample_string):
    assert sample_string == "Hello World!"


def test_sample_dict(sample_dict):
    assert sample_dict["Name"] == "Apple"
    assert sample_dict["Price"] == "100"


def test_combined(sample_string, sample_dict):
    assert sample_string.startswith("Hello")
    assert "Name" in sample_dict
    assert sample_dict["Name"] == "Apple"


# Parameterization for test.
@pytest.mark.parametrize("a, b, expected", [(1, 2, 3), (2, 3, 5), (3, 5, 8)])
def test_addition(a, b, expected):
    assert a + b == expected


@pytest.mark.parametrize(
    "str1, str2, expected",
    [("Hello", "World", "HelloWorld"), ("Py", "Test", "PyTest")],
)
def test_string_concatenation(str1, str2, expected):
    assert str1 + str2 == expected


@pytest.mark.django_db
def test_model_creation():
    test_instance = baker.make(
        Customer,
        name="test_user1",
        dob="2003-04-27",
        email="user1@gmail.com",
        phone_no="123456",
        address="HYD",
        pin_code="100",
        status="alive",
    )
    assert Customer.objects.count() == 1
    assert test_instance.name == "test_user1"