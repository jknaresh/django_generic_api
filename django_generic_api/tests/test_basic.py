import pytest
from test_fixtures import sample_string, sample_dict


def test_sample_string(sample_string):
    assert sample_string == "Hello World!"


def test_sample_dict(sample_dict):
    assert sample_dict["Name"] == "Apple"
    assert sample_dict["Price"] == "100"


def test_combined(sample_string, sample_dict):
    assert sample_string.startswith("Hello")
    assert "Name" in sample_dict
    assert sample_dict["Name"] == "Apple"
