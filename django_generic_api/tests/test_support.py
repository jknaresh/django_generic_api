from django_generic_api.django_generic_api.services import generate_token
from django.contrib.auth.models import Permission, User
import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from api_app.models import Customer


@pytest.fixture
def all_perm_user():
    """
    User with add and view perm.
    """
    user = baker.make(User, username="allpermuser@gmail.com")
    user.set_password("123456")
    user.save()

    perm1 = Permission.objects.get(codename="add_customer")
    perm2 = Permission.objects.get(codename="view_customer")
    user.user_permissions.add(perm1, perm2)
    return user


@pytest.fixture
def save_perm_user():
    """
    User with add perm.
    """
    user = baker.make(User, username="addpermuser@gmail.com")
    user.set_password("123456")
    user.save()

    perm1 = Permission.objects.get(codename="add_customer")
    perm2 = Permission.objects.get(codename="change_customer")
    user.user_permissions.add(perm1, perm2)
    return user


@pytest.fixture
def view_perm_user():
    """
    User with view perm.
    """
    user = baker.make(User, username="viewpermuser@gmail.com")
    user.set_password("123456")
    user.save()

    perm = Permission.objects.get(codename="view_customer")
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def no_perm_user():
    """
    User with no perm.
    """
    user = baker.make(User, username="nopermuser@gmail.com")
    user.set_password("123456")
    user.save()

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
def api_client():
    """Fixture to set up the API client."""
    return APIClient()


@pytest.fixture
def fetch_data_1(db):
    """Fixture for baked Customer model."""
    customer = baker.make(
        Customer,
        name="test_user1",
        dob="2003-04-27",
        email="user1@gmail.com",
        phone_no="123456",
        address="HYD",
        pin_code="100",
        status="alive",
    )
    return customer


@pytest.fixture
def login_user(db):
    login_user = baker.make(
        User,
        username="user@gmail.com",
    )
    login_user.set_password("123456")
    login_user.is_active = True
    login_user.save()

    return login_user


@pytest.fixture
def email_activate_inactive_user_id(db):
    user = baker.make(User, username="inactive@gmail.com")
    user.set_password("123456")
    user.is_active = False
    user.save()
    user_id = user.id

    return user_id
