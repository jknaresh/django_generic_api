import base64
import time

import pytest
from django.contrib.auth.models import Permission
from model_bakery import baker
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# student class instance 1
@pytest.fixture
def student_class_1():
    student_class_1 = baker.make_recipe("demo_app.student_class_1")
    return student_class_1


# customer instance 1
@pytest.fixture
def customer1():
    customer1 = baker.make_recipe("demo_app.customer_1")
    return customer1


# customer instance 2
@pytest.fixture
def customer2():
    customer2 = baker.make_recipe("demo_app.customer_2")
    return customer2


def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return [
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    ]


@pytest.fixture
def all_perm_user():
    """
    User with add and view perm.
    """
    user = baker.make_recipe("demo_app.all_perm_user")

    perm1 = Permission.objects.get(codename="add_customer")
    perm2 = Permission.objects.get(codename="view_customer")
    user.user_permissions.add(perm1, perm2)

    return user


@pytest.fixture
def save_perm_user():
    """
    User with add perm.
    """
    user = baker.make_recipe("demo_app.save_perm_user")

    perm1 = Permission.objects.get(codename="add_customer")
    perm2 = Permission.objects.get(codename="change_customer")
    user.user_permissions.add(perm1, perm2)
    return user


@pytest.fixture
def view_perm_user():
    """
    User with view perm.
    """
    user = baker.make_recipe("demo_app.view_perm_user")

    perm = Permission.objects.get(codename="view_customer")
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def no_perm_user():
    """
    User with no perm.
    """
    user = baker.make_recipe("demo_app.no_perm_user")
    return user


@pytest.fixture
def inactive_user():
    """
    User is inactive
    """
    user = baker.make_recipe("demo_app.inactive_user")
    return user


@pytest.fixture
def all_perm_token(all_perm_user):
    """
    Token for all_perm user
    """
    token = generate_token(all_perm_user)
    access_token = token[0]["access"]

    return access_token


@pytest.fixture
def add_perm_token(save_perm_user):
    """
    Token for add perm user
    """
    token = generate_token(save_perm_user)
    access_token = token[0]["access"]

    return access_token


@pytest.fixture
def view_perm_token(view_perm_user):
    """
    Token for view perm user
    """
    token = generate_token(view_perm_user)
    access_token = token[0]["access"]

    return access_token


@pytest.fixture
def no_perm_token(no_perm_user):
    """
    Token for no perm user
    """
    token = generate_token(no_perm_user)
    access_token = token[0]["access"]

    return access_token


@pytest.fixture
def inactive_user_token(inactive_user):
    """
    Token for all_perm user
    """
    token = generate_token(inactive_user)
    access_token = token[0]["access"]

    return access_token


@pytest.fixture
def api_client():
    """Fixture to set up the API client."""
    return APIClient()


@pytest.fixture
def login_user(db):
    login_user = baker.make_recipe("demo_app.login_user")
    login_user.set_password("123456")
    login_user.is_active = True
    login_user.save()

    return login_user


@pytest.fixture
def inactive_user_id(db):
    user = baker.make_recipe("demo_app.inactive_user_id")
    user.set_password("123456")
    user.is_active = False
    user.save()
    user_id = user.id

    return user_id


@pytest.fixture
def non_existing_user(db):
    user = baker.make_recipe("demo_app.non_existing_user")
    user.set_password("123456")
    user.is_active = False
    user.save()
    user_id = user.id
    user.delete()

    return user_id


@pytest.fixture
def registration_token():
    def token(user_id):
        timestamp = int(time.time())
        token1 = f"{user_id}:{timestamp}"
        encoded_token = base64.urlsafe_b64encode(token1.encode()).decode()
        return encoded_token

    return token
