from django.contrib.auth.models import User
from django_generic_api.tests.demo_app.models import Customer, StudentClass
from model_bakery.recipe import Recipe, foreign_key

# Create instances of a model with predefined field values.

student_class_1 = Recipe(
    StudentClass,
    name = "Class-1",
    address = "HYD",
    count_of_students = 10
)

customer_1 = Recipe(
    Customer,
    name="test_user1",
    email="user1@gmail.com",
    phone_no="123456",
    address="hyderabad",
    std_class = foreign_key(student_class_1)
)

customer_2 = Recipe(
    Customer,
    name="test_user2",
    email="user2@gmail.com",
    phone_no="456789",
    address="HYDERABAD",
)

test_instance = Recipe(Customer, name="instance_1", address="GOA")

all_perm_user = Recipe(
    User,
    username="allpermuser@gmail.com",
    password="123456",
    email="all_perm@test.com",
    first_name="test1",
    last_name="test2",
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
