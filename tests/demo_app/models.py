import uuid

from django.db import models
from django.utils import timezone


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
    name = models.CharField(max_length=63, null=False)
    dob = models.DateField(null=False)  # Date of birth
    email = models.EmailField(null=False)
    phone_no = models.CharField(max_length=15, null=False)
    address = models.CharField(max_length=1023, null=False)  # Address
    pin_code = models.CharField(max_length=6, null=False)  # Postal/ZIP code
    status = models.CharField(max_length=5)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "demo_app"
