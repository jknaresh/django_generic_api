import random
from django.contrib.auth import get_user_model
from django_generic_api.tests.demo_app.models import (
    Customer,
    StudentClass,
    JobModel,
    UserProfile,
    Book,
)
from model_bakery.recipe import Recipe, foreign_key

User = get_user_model()

# Create instances of a model with predefined field values.

student_class_1 = Recipe(
    StudentClass, name="Class-1", address="HYD", count_of_students=10
)

customer_1 = Recipe(
    Customer,
    name="test_user1",
    email="user1@gmail.com",
    phone_no="123456",
    address="hyderabad",
    std_class=foreign_key(student_class_1),
)

customer_2 = Recipe(
    Customer,
    name="test_user2",
    email="user2@gmail.com",
    phone_no="456789",
    address="HYDERABAD",
)

test_instance = Recipe(Customer, name="instance_1", address="GOA")

job_instance = Recipe(
    JobModel,
    company_name="Client Server",
    location="Hyderabad",
    owner_name="ABCD EFGH",
)

job_instance2 = Recipe(
    JobModel,
    company_name="Apple",
    location="Hyderabad",
    owner_name="WXYZ",
)

all_perm_user = Recipe(
    User,
    username="allpermuser@gmail.com",
    password="123456",
    email="all_perm@test.com",
    first_name="test1",
    last_name="test2",
    job_at=foreign_key(job_instance),
)

book1 = Recipe(Book, name="book1", author="author1")

book2 = Recipe(Book, name="book2", author="author2")

user1 = Recipe(
    User,
    username="user@test.com",
    password="123456",
    email=lambda: f"user_{random.randint(0, 10)}@test.com",
    first_name="user",
    last_name="abcd",
    job_at=foreign_key(job_instance),
)


user_profile = Recipe(
    UserProfile,
    user=foreign_key(user1),
    birthday="2003-04-27",
    gender="M",
    primary_number="9676416451",
    secondary_number="7729928022",
    address="India",
    city="Hyd",
    zip="500074",
    fav_book=foreign_key(book1),
)

save_perm_user = Recipe(
    User, username="addpermuser@gmail.com", password="123456"
)

view_perm_user = Recipe(
    User, username="viewpermuser@gmail.com", password="123456"
)

no_perm_user = Recipe(User, username="nopermuser@gmail.com", password="123456")

login_user = Recipe(
    User,
    username="user@gmail.com",
)

inactive_user_id = Recipe(
    User,
    username="inactive@gmail.com",
)

non_existing_user = Recipe(
    User,
    username="non_existing_user@gmail.com",
)

inactive_user = Recipe(
    User, username="inactiveuser@gmail.com", is_active=False
)
