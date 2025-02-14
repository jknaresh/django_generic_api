import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _


class StudentClass(models.Model):

    name = models.CharField(max_length=15, db_column="student_name")
    address = models.CharField(max_length=15, verbose_name="related address")
    count_of_students = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Student Class"

    def __str__(self):
        return self.name


class BaseClass(models.Model):
    slug = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=False
    )
    inserted_timestamp = models.DateTimeField(default=timezone.now, null=False)
    update_timestamp = models.DateTimeField(null=True, blank=True)
    end_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.slug)

    @classmethod
    def get_queryset(cls, **kwargs):
        return cls.objects.filter(**kwargs)


class Customer(BaseClass):
    name = models.CharField(
        max_length=63, null=False, verbose_name="customer_name"
    )
    dob = models.DateField(null=False)  # Date of birth
    email = models.EmailField(null=False)
    phone_no = models.CharField(max_length=15, null=False)
    address = models.CharField(max_length=1023, null=False)  # Address
    pin_code = models.CharField(max_length=6, null=False)  # Postal/ZIP code
    status = models.CharField(max_length=5)
    is_alive = models.BooleanField(default=True, null=False)
    std_class = models.ForeignKey(
        StudentClass,
        on_delete=models.SET_NULL,
        null=True,
        related_name="class_of_student",
        db_column="class_student",
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "demo_app"


class JobModel(models.Model):
    company_name = models.CharField(
        max_length=15, blank=True, null=True, db_column="company_name_column"
    )
    location = models.CharField(max_length=8, blank=True, null=True)
    owner_name = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.company_name


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email as the unique identifier.
    """

    email = models.EmailField(unique=True, verbose_name=_("emailaddr"))
    username = models.CharField(max_length=150, verbose_name=_("username"))
    first_name = models.CharField(max_length=150, verbose_name=_("fname"))
    last_name = models.CharField(max_length=150, verbose_name=_("lname"))
    is_active = models.BooleanField(
        default=True, verbose_name=_("active status")
    )
    is_staff = models.BooleanField(
        default=False, verbose_name=_("staff status")
    )
    job_at = models.ForeignKey(
        JobModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    field_db = models.CharField(
        max_length=7, db_column="db field", null=True, blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email


class Book(models.Model):

    name = models.CharField(max_length=32, null=True, blank=True)
    author = models.CharField(max_length=32, null=True, blank=True)


class UserProfile(models.Model):

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    user = models.OneToOneField(
        CustomUserModel, unique=True, on_delete=models.SET_NULL, null=True
    )
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True
    )
    primary_number = models.CharField(max_length=32, null=False, blank=False)
    secondary_number = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.IntegerField(null=True, blank=True)
    fav_book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, null=True, related_name="liked_book"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s profile"
