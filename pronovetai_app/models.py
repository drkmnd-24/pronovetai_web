from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validated_image_size(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(_('Maximum file size allowed is 5MB'))


class User(AbstractUser):
    USER_ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]
    role = models.CharField(
        max_length=20,
        choices=USER_ROLE_CHOICES,
        default='user',
        help_text='Designated role: admin, manager or user'
    )

    def __str__(self):
        return self.username


class Contact(models.Model):
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts'
    )
    title = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    position = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    fax_number = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        # Return full name if available, else email.
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}'.strip()
        return self.email


class Address(models.Model):
    street_address = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.street_address} - {self.city}'


class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='buildings'
    )
    year_built = models.PositiveIntegerField()
    is_for_sale = models.BooleanField(default=False)
    is_peza_certified = models.BooleanField(default=False)
    is_strata = models.BooleanField(default=False)
    grade = models.CharField(max_length=50)
    typical_floor_plate_area = models.DecimalField(max_digits=10, decimal_places=2)
    floor_to_ceiling_height = models.DecimalField(max_digits=5, decimal_places=2)
    number_of_floors = models.PositiveIntegerField()
    parking_floors = models.PositiveIntegerField()
    passenger_elevators = models.PositiveIntegerField()
    service_elevators = models.PositiveIntegerField()
    ac_type = models.CharField(max_length=50)
    ac_operating_hours_charge = models.DecimalField(max_digits=10, decimal_places=2)
    office_rent = models.DecimalField(max_digits=10, decimal_places=2)
    association_dues = models.DecimalField(max_digits=10, decimal_places=2)
    floor_area_ratio = models.DecimalField(max_digits=4, decimal_places=2)
    gross_floor_area = models.DecimalField(max_digits=10, decimal_places=2)
    gross_leasable_area = models.DecimalField(max_digits=10, decimal_places=2)
    building_type = models.CharField(max_length=50)
    space_for_lease = models.DecimalField(max_digits=10, decimal_places=2)
    space_for_sale = models.DecimalField(max_digits=10, decimal_places=2)
    space_occupied = models.DecimalField(max_digits=10, decimal_places=2)

    # New: Relationship to Contact(s). A building can have multiple contacts.
    contacts = models.ManyToManyField('Contact', blank=True, related_name='buildings')

    # Log fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='buildings_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    MARKETING_STATUS_CHOICES = [
        ('lease', 'For Lease'),
        ('sale', 'For Sale'),
        ('lease_sale', 'For Lease and For Sale'),
        ('unknown', "Don't know"),
    ]
    VACANCY_STATUS_CHOICES = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
    ]

    name = models.CharField(max_length=255)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='units')
    floor = models.IntegerField()
    marketing_status = models.CharField(max_length=20, choices=MARKETING_STATUS_CHOICES, default='unknown')
    vacancy_status = models.CharField(max_length=20, choices=VACANCY_STATUS_CHOICES, default='vacant')
    foreclosed = models.BooleanField(default=False)
    contact_information = models.CharField(max_length=255)
    # Unit details
    gross_floor_area = models.DecimalField(max_digits=10, decimal_places=2)
    net_floor_area = models.DecimalField(max_digits=10, decimal_places=2)
    floor_to_ceiling_height = models.DecimalField(max_digits=5, decimal_places=2)
    ceiling_condition = models.CharField(max_length=100)
    floor_condition = models.CharField(max_length=100)
    partition_condition = models.CharField(max_length=100)
    # Current lease details
    lease_commencement_date = models.DateField(null=True, blank=True)
    lease_expiry_date = models.DateField(null=True, blank=True)
    # For lease details
    asking_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    allocated_parking_slot = models.PositiveIntegerField(null=True, blank=True)
    price_per_parking_slot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimum_period = models.CharField(max_length=50, null=True, blank=True)
    escalation_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rent_free = models.CharField(max_length=50, null=True, blank=True)
    dues = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # For sale details
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_parking = models.CharField(max_length=50, null=True, blank=True)
    # Additional notes
    unit_notes = models.TextField(null=True, blank=True)

    def clean(self):
        if self.net_floor_area > self.gross_floor_area:
            raise ValidationError(_('Net Floor area cannot be greater than gross floor area'))

        if self.lease_commencement_date and self.lease_expiry_date:
            if self.lease_commencement_date > self.lease_expiry_date:
                raise ValidationError(_('Lease commencement date must be before lease expiry date'))

    def __str__(self):
        return f"{self.name} ({self.building.name})"


class Company(models.Model):
    name = models.CharField(max_length=255)
    # Related to building details
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='companies')
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='companies'
    )
    industry = models.CharField(max_length=100)
    # Affiliations
    building_affiliations = models.ManyToManyField(Building, related_name='affiliated_companies', blank=True)
    unit_affiliations = models.ManyToManyField(Unit, related_name='affiliated_companies', blank=True)
    contact = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ODForm(models.Model):
    TYPE_OF_CALL_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    SOURCE_OF_CALL_CHOICES = [
        ('newspaper', 'Newspaper'),
        ('old_client', 'Old Client'),
        ('online_marketing', 'Online Marketing'),
        ('referral', 'Referral'),
        ('signage', 'Signage'),
        ('website', 'Website'),
        ('yellow_pages', 'Yellow Pages'),
        ('others', 'Others'),
    ]

    TYPE_OF_CALLER_CHOICES = [
        ('broker', 'Broker'),
        ('direct', 'Direct Buyer / Lease'),
    ]

    INTENT_CHOICES = [
        ('rent', 'To Rent'),
        ('buy', 'To Buy'),
        ('both', 'Both'),
    ]

    PURPOSE_CHOICES = [
        ('expanding', 'Expanding'),
        ('relocating', 'Relocating'),
        ('new_office', 'New Office'),
        ('consolidating', 'Consolidating'),
        ('downsizing', 'Downsizing'),
        ('upgrading', 'Upgrading'),
        ('expanding_retaining', 'Expanding while retaining current office'),
        ('others', 'Others'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('done_deal', 'Done Deal'),
    ]
    date = models.DateTimeField()
    contact = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='od_forms')
    call_taken_by = models.CharField(max_length=255, null=True, blank=True)
    type_of_call = models.CharField(max_length=10, choices=TYPE_OF_CALL_CHOICES)
    source_of_call = models.CharField(max_length=20, choices=SOURCE_OF_CALL_CHOICES)
    type_of_caller = models.CharField(max_length=20, choices=TYPE_OF_CALLER_CHOICES)
    intent = models.CharField(max_length=10, choices=INTENT_CHOICES)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    size_minimum = models.DecimalField(max_digits=10, decimal_places=2)
    budget_minimum = models.DecimalField(max_digits=10, decimal_places=2)
    prefered_location = models.CharField(max_length=100)
    size_maximum = models.DecimalField(max_digits=10, decimal_places=2)
    budget_maximum = models.DecimalField(max_digits=10, decimal_places=2)
    started_scouting = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    account_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'is_staff': True},
        related_name='od_forms'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.size_minimum > self.size_maximum:
            raise ValidationError(_('Size minimum cannot be greater than size maximum'))

        if self.budget_minimum > self.budget_maximum:
            raise ValidationError(_('Budget minimum cannot be greater than budget maximum'))

    def __str__(self):
        return f'OD Form {self.id} - {self.contact}'


class BuildingImage(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='building_images/', validators=[validated_image_size])

    def clean(self):
        if self.building and not self.pk and self.building.images.count() >= 3:
            raise ValidationError(_('Maximum of 3 images allowed per building'))

    def __str__(self):
        return f'Image for {self.building.name}'


class UnitImage(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='unit_images/', validators=[validated_image_size])

    def clean(self):
        if self.unit and not self.pk and self.unit.images.count() >= 3:
            raise ValidationError(_('Maximum of 3 images allowed per building'))

    def __str__(self):
        return f'Image for {self.unit.name}'
