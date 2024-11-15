import pytest
from test_fixtures import func


def test_answer():
    assert func(3) == 4