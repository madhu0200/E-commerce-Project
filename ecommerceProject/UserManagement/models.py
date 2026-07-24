import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Users(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'customer'
        ADMIN = 'ADMIN', 'admin'
        SELLER = 'SELLER', 'seller'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True,editable=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    # Django uses 'is_active' internally for auth checks
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} - {self.role}"


class BaseAddress(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    door_no = models.CharField(max_length=50)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=30, default='INDIA')

    class Meta:
        abstract = True


class CustomerAddress(BaseAddress):
    class AddressType(models.TextChoices):
        HOME = 'HOME', 'home'
        WORK = 'WORK', 'work'
        OTHER = 'OTHER', 'other'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_addresses',
        limit_choices_to={'role': 'CUSTOMER'}
    )

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address_type = models.CharField(choices=AddressType.choices, default=AddressType.HOME, max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customer_addresses'
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        # If this is the user's first address, force it to be default
        if not CustomerAddress.objects.filter(user=self.user).exists():
            self.is_default = True

        # If saving as default, reset other default addresses for this user
        if self.is_default:
            CustomerAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city} - {self.address_type}"


class SellerAddress(BaseAddress):
    class AddressPurpose(models.TextChoices):
        WAREHOUSE = 'WAREHOUSE', 'Warehouse / Pickup Point'
        REGISTERED_OFFICE = 'REGISTERED_OFFICE', 'Registered Office'
        RETURN_LOCATION = 'RETURN_LOCATION', 'Return Location'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_addresses',
        limit_choices_to={'role': 'SELLER'}
    )
    company_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    purpose = models.CharField(max_length=20, choices=AddressPurpose.choices, default=AddressPurpose.WAREHOUSE)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'seller_addresses'

    def __str__(self):
        return f"{self.company_name} [{self.purpose}] - {self.city}"