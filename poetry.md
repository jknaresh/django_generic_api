# Poetry utilization

## Introduction

- Poetry is a tool for package management that simplifies the process of
  creating, managing, and publishing Python packages.

---

## Installation

### Windows

- To install Poetry on Windows, run one of the following commands in the
  terminal:

```bash 
pip install poetry
```

or

```bash 
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Linux, macOS, WSL

- To install Poetry on Linux, macOS, or WSL, run the following command in the
  terminal:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Verify Installation

- To verify if poetry is successfully installed, run the following command:

```bash
poetry --version

# output: Poetry (version 1.8.5)
```

---

## Installing Dependencies

- To install the dependencies defined in your project, run the command as

```bash
poetry install
```

- When this command is executed, it resolves and installs the dependencies that
  are listed in `pyproject.toml` file.

---

## Specifying Dependencies

### Adding Dependencies

- To add a new dependency, you can use the poetry add command:

```bash
poetry add pendulum
```

- This command adds the dependency to `pyproject.toml` with its compatible
  version number.
- Additionally, it updates the `poetry.lock` file, which contains locked
  versions and file hashes to ensure consistent installations across
  environments.

### To add dependencies for specific purposes:

- Testing:

```bash
poetry add pytest --group test
```

- To run tests, use:

```bash 
poetry run pytest -v
```

- Development:

```bash
poetry add black --group dev
```

---

## Running Commands:

- Use the prefix `poetry run` to execute commands within the Poetry
  environment.

```bash
# example:

- To commit your files:

poetry run git add <file_name>
poetry run git commit -m "<commit_message>"
```

## Requirements File

- If you've updated the project's dependencies, update the requirements.txt
  file using:

```bash
poetry export --output requirements.txt
```

## Publishing the package

### Update the Version

- Before publishing, update the version number in the `tool.poetry` section of
  the `pyproject.toml` file.

### Build the Package

- Package the project using:

```bash 
poetry build
```

- Poetry uses the information specified in the `pyproject.toml` file to create
  the package.

### Ensure You Have a PyPI Account

- If you don't have a PyPI account, create one here.

### Generate a PyPi API token

- Log in to your PyPI account.
- Go to your Account settings.
- Scroll down to the "API tokens" section and create a new token.
- Assign the token the appropriate scope.

### Configure Poetry with the API Token

- Use Poetry to configure the token for authentication

```bash
poetry config pypi-token.pypi <your-api-token>
```

- Now to publish, follow command as

```bash
poetry publish
```