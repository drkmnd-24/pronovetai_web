from django.db import models
from django.contrib.auth.models import User

class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    year_built = models.PositiveIntegerField()
    for_sale = models.BooleanField(default=False)
    peza_certified = models.BooleanField(default=False)
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
    # Log fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='buildings_created')
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

    def __str__(self):
        return f"{self.name} ({self.building.name})"


class Company(models.Model):
    name = models.CharField(max_length=255)
    # Related to building details
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='companies')
    street_address = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    # Affiliations
    building_affiliations = models.ManyToManyField(Building, related_name='affiliated_companies', blank=True)
    unit_affiliations = models.ManyToManyField(Unit, related_name='affiliated_companies', blank=True)
    contact = models.CharField(max_length=255)

    def __str__(self):
        return self.name
