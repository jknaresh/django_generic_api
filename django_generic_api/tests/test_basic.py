import pytest
from model_bakery import baker

from django_generic_api.tests.demo_app.models import Customer
from fixtures.basic import sample_string, sample_dict


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


# to test the model created in custom app "demo_app"
@pytest.mark.django_db
def test_model_creation():
    test_instance = baker.make_recipe("demo_app.test_instance")

    assert Customer.objects.count() == 1
    assert test_instance.name == "instance_1"
    assert test_instance.address == "GOA"
