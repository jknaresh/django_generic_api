# Fixtures are used to set up the preconditions or test environment required
# for tests.
# They help in avoiding repeating code by providing reusable components that tests can rely on.

import pytest

@pytest.fixture
def sample_string():
    return "Hello World!"

@pytest.fixture
def sample_dict():
    return {"Name": "Apple", "Price": "100"}
