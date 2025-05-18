from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class MyDateTimeField(models.DateTimeField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, str):
            dt = parse_datetime(value)
            if dt is None:
                return super().from_db_value(value, expression, connection)
            if settings.USE_TZ:
                dt = timezone.make_aware(dt, self._get_connection_timezone(connection))
            return dt
        return value

    def _get_connection_timezone(self, connection):
        return getattr(connection, 'timezone', timezone.get_current_timezone())


def validated_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(_('Maximum file size allowed is 5MB'))


class UserType(models.Model):
    id = models.AutoField(primary_key=True, db_column='user_type_id')
    description = models.CharField(max_length=255, db_column='user_type_desc')
    created_at = models.DateTimeField(db_column='user_type_created')

    class Meta:
        db_table = 'pt_user_types'
        managed = False

    def __str__(self):
        return self.description


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, created_by=None, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        extra_fields.setdefault('date_joined', timezone.now())
        user = self.model(
            username=username,
            created_by=created_by,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    """
    A truly custom user model pointing at your `pt_users` table,
    with no BooleanField columns for is_active/is_staff in the DB.
    """
    id = models.AutoField(primary_key=True, db_column='user_id')
    username = models.CharField(max_length=150, unique=True, db_column='user_login')
    password = models.CharField(max_length=128, db_column='user_pass')
    email = models.EmailField(db_column='user_email', blank=True)
    first_name = models.CharField(max_length=150, db_column='user_first_name', blank=True)
    last_name = models.CharField(max_length=150, db_column='user_last_name', blank=True)
    date_joined = MyDateTimeField(
        db_column='user_registered',
        default=timezone.now,
        help_text='When this user was created'
    )
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='created_user_id',
        related_name='users_created')
    created_date = models.DateTimeField(
        db_column='created_date',
        auto_now_add=True
    )
    edited_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='edited_user_id',
        related_name='users_edited')
    edited_date = models.DateTimeField(db_column='edited_date', auto_now=True)

    # link to your user-type table
    user_type = models.ForeignKey(
        'UserType',
        on_delete=models.SET_NULL,
        null=True,
        db_column='user_type_id',
        related_name='users'
    )

    # **no** BooleanField columns in the DB; just Python flags:
    is_active = True
    is_staff = False

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'pt_users'
        managed = False

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.username

    # Django (and SimpleJWT) will check these:
    def has_perm(self, perm, obj=None):
        # only “staff” can do admin-style things
        return bool(self.is_staff)

    def has_module_perms(self, app_label):
        return bool(self.is_staff)

    def __str__(self):
        return self.username


class UserLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logs',
        db_column='user_id'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pt_user_logs'
        managed = False

    def __str__(self):
        return f'Log for {self.user.username} at {self.timestamp}'


class Address(models.Model):
    street_address = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)

    class Meta:
        db_table = 'pt_addresses'
        managed = False

    def __str__(self):
        return f'{self.street_address or ""} - {self.city}'


class Contact(models.Model):
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts',
        db_column='company_id'
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
    CONTACT_TYPE_CHOICES = [
        ('property_manager', 'Property Manager'),
        ('tenant', 'Tenant'),
        ('agent', 'Agent'),
        ('owner', 'Owner'),
        ('owner_representative', 'Owner Representative'),
        ('pta', 'PTA'),
        ('others', 'Others'),
    ]
    contact_type = models.CharField(
        max_length=50, choices=CONTACT_TYPE_CHOICES, blank=True, null=True
    )

    class Meta:
        db_table = 'pt_contacts'
        managed = False

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email


class Building(models.Model):
    id = models.AutoField(primary_key=True, db_column='building_id')
    name = models.CharField(max_length=255)
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='buildings',
        db_column='address_id'
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
    contacts = models.ManyToManyField(
        Contact,
        blank=True,
        related_name='buildings',
        db_table='pt_building_contacts'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='buildings_created',
        db_column='created_user_id'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_date')
    last_edited = models.DateTimeField(auto_now=True, db_column='edited_date')

    class Meta:
        db_table = 'pt_buildings'
        managed = False

    def __str__(self):
        return self.name


class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_column='unit_id')
    name = models.CharField(max_length=255)
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='units',
        db_column='building_id'
    )
    floor = models.IntegerField()
    MARKETING_STATUS_CHOICES = [
        ('lease', 'For Lease'),
        ('sale', 'For Sale'),
        ('lease_sale', 'For Lease and For Sale'),
        ('unknown', "Don't know"),
    ]
    marketing_status = models.CharField(
        max_length=20,
        choices=MARKETING_STATUS_CHOICES,
        default='unknown'
    )
    VACANCY_STATUS_CHOICES = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
    ]
    vacancy_status = models.CharField(
        max_length=20,
        choices=VACANCY_STATUS_CHOICES,
        default='vacant'
    )
    foreclosed = models.BooleanField(default=False)
    contact_information = models.CharField(max_length=255)
    gross_floor_area = models.DecimalField(max_digits=10, decimal_places=2)
    net_floor_area = models.DecimalField(max_digits=10, decimal_places=2)
    floor_to_ceiling_height = models.DecimalField(max_digits=5, decimal_places=2)
    ceiling_condition = models.CharField(max_length=100)
    floor_condition = models.CharField(max_length=100)
    partition_condition = models.CharField(max_length=100)
    lease_commencement_date = models.DateField(null=True, blank=True)
    lease_expiry_date = models.DateField(null=True, blank=True)
    asking_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    allocated_parking_slot = models.PositiveIntegerField(null=True, blank=True)
    price_per_parking_slot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimum_period = models.CharField(max_length=50, null=True, blank=True)
    escalation_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rent_free = models.CharField(max_length=50, null=True, blank=True)
    dues = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_parking = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'pt_units'
        managed = False

    def clean(self):
        if self.net_floor_area > self.gross_floor_area:
            raise ValidationError(_('Net floor area cannot exceed gross floor area'))
        if self.lease_commencement_date and self.lease_expiry_date and self.lease_commencement_date > self.lease_expiry_date:
            raise ValidationError(_('Lease commencement must be before lease expiry'))

    def __str__(self):
        return f"{self.name} ({self.building.name})"


class Company(models.Model):
    id = models.AutoField(primary_key=True, db_column='company_id')
    name = models.CharField(max_length=255)
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='companies',
        db_column='building_id'
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='companies',
        db_column='address_id'
    )
    industry = models.CharField(max_length=100)
    building_affiliations = models.ManyToManyField(
        Building,
        related_name='affiliated_companies',
        blank=True,
        db_table='pt_company_building_affiliations'
    )
    unit_affiliations = models.ManyToManyField(
        Unit,
        related_name='affiliated_companies',
        blank=True,
        db_table='pt_company_unit_affiliations'
    )

    class Meta:
        db_table = 'pt_companies'
        managed = False

    def __str__(self):
        return self.name


class ODForm(models.Model):
    id = models.AutoField(primary_key=True, db_column='odform_id')
    date = models.DateTimeField(db_column='date')
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='od_forms',
        db_column='contact_id'
    )
    call_taken_by = models.CharField(max_length=255, null=True, blank=True)
    TYPE_OF_CALL_CHOICES = [('inbound', 'Inbound'), ('outbound', 'Outbound')]
    type_of_call = models.CharField(max_length=10, choices=TYPE_OF_CALL_CHOICES)
    SOURCE_OF_CALL_CHOICES = [
        ('newspaper', 'Newspaper'), ('old_client', 'Old Client'), ('online_marketing', 'Online Marketing'),
        ('referral', 'Referral'), ('signage', 'Signage'), ('website', 'Website'), ('yellow_pages', 'Yellow Pages'),
        ('others', 'Others'),
    ]
    source_of_call = models.CharField(max_length=20, choices=SOURCE_OF_CALL_CHOICES)
    TYPE_OF_CALLER_CHOICES = [('broker', 'Broker'), ('direct', 'Direct Buyer / Lease')]
    type_of_caller = models.CharField(max_length=20, choices=TYPE_OF_CALLER_CHOICES)
    INTENT_CHOICES = [('rent', 'To Rent'), ('buy', 'To Buy'), ('both', 'Both')]
    intent = models.CharField(max_length=10, choices=INTENT_CHOICES)
    PURPOSE_CHOICES = [
        ('expanding', 'Expanding'), ('relocating', 'Relocating'), ('new_office', 'New Office'),
        ('consolidating', 'Consolidating'), ('downsizing', 'Downsizing'), ('upgrading', 'Upgrading'),
        ('expanding_retaining', 'Expanding while retaining'), ('others', 'Others'),
    ]
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
        null=True,
        blank=True,
        related_name='od_forms',
        db_column='account_manager_id'
    )
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('done_deal', 'Done Deal')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'pt_odforms'
        managed = False

    def clean(self):
        if self.size_minimum > self.size_maximum:
            raise ValidationError(_('Size minimum cannot exceed size maximum'))
        if self.budget_minimum > self.budget_maximum:
            raise ValidationError(_('Budget minimum cannot exceed budget maximum'))

    def __str__(self):
        return f"OD Form {self.id} – {self.contact}"


class BuildingImage(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='images',
        db_column='building_id'
    )
    image = models.ImageField(upload_to='building_images/', validators=[validated_image_size])

    class Meta:
        db_table = 'pt_building_images'
        managed = False

    def __str__(self):
        return f"Image for {self.building.name}"


class UnitImage(models.Model):
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='images',
        db_column='unit_id'
    )
    image = models.ImageField(upload_to='unit_images/', validators=[validated_image_size])

    class Meta:
        db_table = 'pt_unit_images'
        managed = False

    def __str__(self):
        return f"Image for {self.unit.name}"
