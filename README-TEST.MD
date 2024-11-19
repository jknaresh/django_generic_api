## Setting Up Your Environment.

```bash
pip install pytest==8.3.3
```

## To run all test cases:

- Edit the DJANGO_SETTINGS_MODULE in the pytest.ini file to point to your_project.settings.
- From the root folder where the pytest.ini file is located, run the following command in the command line:
```bash
pytest
```

- Ensure you have set up the path to the test file correctly, including any necessary parameters.

## Configuring Pytest for individual file.
- To configure pytest, follow these steps:

### In PyCharm:
- Add a new configuration for pytest.
- Select your Python environment.
- Set the path to the test file.
- Add any necessary arguments for pytest.
- Apply and save the configuration.

## Running Tests

- To run a Test case file, follow these steps:

### In PyCharm:
- Create a pytest configuration for the file if it does not already exist.
- Use the debugger to run the test case file.
