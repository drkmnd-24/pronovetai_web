from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .fields import BlankZeroIntegerField, BlankZeroDecimalField


class MyDateTimeField(models.DateTimeField):
    def get_db_converters(self, connection):
        # Only run our from_db_value converter.
        return [self.from_db_value]

    def from_db_value(self, value, expression, connection):
        """
        Turn MySQL-returned strings into real datetimes once and for all.
        Treat any '0000-00-00...' value as None.
        """
        if value is None:
            return None

        # MySQL zero‐date sentinel:
        if isinstance(value, str) and value.startswith('0000-00-00'):
            return None

        # Parse normal string form into datetime
        if isinstance(value, str):
            dt = parse_datetime(value)
            if dt is None:
                # fallback to Django’s normal parsing if parse_datetime fails
                return super().to_python(value)
            if settings.USE_TZ:
                # make it timezone‐aware, using the DB’s tz if available
                tz = getattr(connection, "timezone", timezone.get_current_timezone())
                dt = timezone.make_aware(dt, tz)
            return dt

        # Already a datetime instance
        return value

    def to_python(self, value):
        """
        Also catch zero‐dates in Python-land (e.g. during model deserialization).
        """
        if isinstance(value, str) and value.startswith('0000-00-00'):
            return None
        return super().to_python(value)


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
    def _require_user_type(self, extra):
        val = extra.get('user_type')
        if isinstance(val, UserType):
            return

        if isinstance(val, (int, str)) and str(val).isdigit():
            try:
                extra['user_type'] = UserType.objects.get(pk=int(val))
                return
            except ObjectDoesNotExist:
                raise ValueError(f'UserType id={val} does not exist')

        if isinstance(val, str):
            obj = UserType.objects.filter(description__iexact=val).first()
            if obj:
                extra['user_type'] = obj
                return

        default = UserType.objects.first()
        if default:
            extra['user_type'] = default
        else:
            raise ValueError(
                'Please create at least one UserType row '
                'or pass a valid user_type during createsuperuser.'
            )

    def create_user(self, username, password=None, created_by=None, **extra):
        if not username:
            raise ValueError("Username must be set")

        self._require_user_type(extra)

        extra.setdefault('date_joined', timezone.now())

        user = self.model(
            username=username,
            created_by=created_by,
            **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)

        self._require_user_type(extra)

        return self.create_user(username, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, db_column='user_id')
    username = models.CharField(max_length=150, unique=True, db_column='user_login')
    password = models.CharField(max_length=128, db_column='user_pass')
    email = models.EmailField(db_column='user_email', blank=True)
    first_name = models.CharField(max_length=150, db_column='user_first_name', blank=True)
    last_name = models.CharField(max_length=150, db_column='user_last_name', blank=True)
    last_login = MyDateTimeField(db_column='last_login', null=True, blank=True)
    date_joined = MyDateTimeField(db_column='user_registered', default=timezone.now)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                   db_column='created_user_id', related_name='users_created')
    created_date = MyDateTimeField(db_column='created_date', auto_now_add=True)
    edited_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                  db_column='edited_user_id', related_name='users_edited')
    edited_date = MyDateTimeField(db_column='edited_date', auto_now=True)
    user_type = models.ForeignKey(UserType, verbose_name='User type (ID or label)',
                                  on_delete=models.SET_NULL, null=True,
                                  db_column='user_type_id', related_name='users')
    is_active = models.BooleanField(default=True, db_column='is_active')
    is_staff = models.BooleanField(default=False, db_column='is_staff')

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'user_type']

    class Meta:
        db_table = 'pt_users'
        managed = False

    def __str__(self):
        return self.username


class CustomerUserManager(BaseUserManager):
    def _require_user_type(self, extra):
        if extra.get('user_type'):
            return
        default = UserType.objects.first()
        if default is None:
            raise ValueError('No UserType rows exist - create one or pass user_type')
        extra['user_type'] = default

    def create_user(self, username, password=None, created_by=None, **extra):
        if not username:
            raise ValueError('Username must be set')
        self._require_user_type(extra)

        extra.setdefault('date__joined', timezone.now())

        user = self.model(username=username, created_by=created_by, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)

        self._require_user_type(extra)

        if not extra['is_staff'] or not extra['is_superuser']:
            raise ValueError('Super-user requires is_staff=True and is_superuser=True')
        return self.create_user(username, password, **extra)


class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs', db_column='user_id')
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


# ------------------------------------------------------------
#  Lookup table (unchanged – we keep it for later use)
# ------------------------------------------------------------
class ContactType(models.Model):
    id = models.AutoField(primary_key=True, db_column='contact_type_id')
    description = models.CharField(max_length=255, db_column='contact_type_desc')

    class Meta:
        db_table = 'pt_contact_types'
        managed = False  # <- legacy table, no migrations

    def __str__(self):
        return self.description


# ------------------------------------------------------------
#  Main contact table – **no contact_type column here**
# ------------------------------------------------------------
class Contact(models.Model):
    id = models.AutoField(primary_key=True, db_column='contact_id')

    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        db_column='company_id',
        related_name='contacts',
    )

    # personal info
    title = models.CharField(max_length=100, db_column='contact_title', blank=True, null=True)
    first_name = models.CharField(max_length=100, db_column='contact_first_name', blank=True, null=True)
    last_name = models.CharField(max_length=100, db_column='contact_last_name', blank=True, null=True)
    files_as = models.CharField(max_length=255, db_column='contact_files_as', blank=True, null=True)
    position = models.CharField(max_length=100, db_column='contact_position', blank=True, null=True)

    # comms
    phone_number = models.CharField(max_length=20, db_column='contact_phone', blank=True, null=True)
    mobile_number = models.CharField(max_length=20, db_column='contact_mobile', blank=True, null=True)
    fax_number = models.CharField(max_length=20, db_column='contact_fax', blank=True, null=True)
    email = models.CharField(max_length=254, db_column='contact_email', blank=True, null=True)

    notes = models.TextField(db_column='contact_notes', blank=True, null=True)

    # ----------------------------------------------------------------
    # There is **no contact_type column** in pt_contacts, so we remove
    # any field that would make Django query it.
    # ----------------------------------------------------------------

    class Meta:
        db_table = 'pt_contacts'
        managed = False  # legacy / read-only

    @property
    def full_name(self):
        return f'{self.first_name or ""} {self.last_name or ""}'.strip() or None

    def __str__(self):
        return self.full_name or self.email or str(self.id)


class Building(models.Model):
    id = models.AutoField(primary_key=True, db_column='building_id')

    # ---------- basic facts ----------
    name = models.CharField(max_length=255, db_column='building_name')
    year_built = BlankZeroIntegerField(
        db_column='building_year_built', null=True, blank=True
    )
    is_peza_certified = models.BooleanField(db_column='building_peza')
    is_strata = models.BooleanField(db_column='building_strata')

    # look-up tables (same as before)
    grade = models.CharField(
        max_length=3,
        db_column='building_grade',  # <- matches MySQL
        blank=True,
        null=True,
    )
    building_type = models.ForeignKey(
        'BuildingType',
        on_delete=models.SET_NULL,
        null=True,
        db_column='building_type',  # <- matches MySQL
        related_name='+'
    )

    # ---------- size / vertical transport ----------
    typical_floor_plate_area = BlankZeroDecimalField(
        max_digits=10, decimal_places=2, db_column='building_plate_area',
        null=True, blank=True
    )
    floor_to_ceiling_height = BlankZeroDecimalField(
        max_digits=5, decimal_places=2, db_column='building_f2ch',
        null=True, blank=True
    )
    number_of_floors = BlankZeroIntegerField(db_column='building_total_level',
                                             null=True, blank=True)
    parking_floors = BlankZeroIntegerField(db_column='building_parking_level',
                                           null=True, blank=True)
    passenger_elevators = BlankZeroIntegerField(db_column='building_pass_lift',
                                                null=True, blank=True)
    service_elevators = BlankZeroIntegerField(db_column='building_service_lift',
                                              null=True, blank=True)

    # ---------- air-con & rents ----------
    ac_type = models.CharField(max_length=50, db_column='building_ac_type')
    ac_operating_hours_charge = BlankZeroDecimalField(
        max_digits=10, decimal_places=2, db_column='building_ac_ophrs_chg',
        null=True, blank=True
    )
    office_rent = BlankZeroDecimalField(max_digits=10, decimal_places=2,
                                        db_column='building_office_rent',
                                        null=True, blank=True)
    association_dues = BlankZeroDecimalField(max_digits=10, decimal_places=2,
                                             db_column='building_assoc_dues',
                                             null=True, blank=True)

    floor_area_ratio = BlankZeroDecimalField(max_digits=6, decimal_places=2,
                                             db_column='building_far',
                                             null=True, blank=True)
    gross_floor_area = models.DecimalField(max_digits=10, decimal_places=2, db_column='building_gfa')
    gross_leasable_area = BlankZeroDecimalField(max_digits=12, decimal_places=2,
                                                db_column='building_gla',
                                                null=True, blank=True)

    # ---------- address split over four columns ----------
    address_street = models.CharField(max_length=255, db_column='building_address_street', blank=True, null=True)
    address_brgy = models.CharField(max_length=100, db_column='building_address_brgy', blank=True, null=True)
    address_city = models.CharField(max_length=100, db_column='building_address_city', blank=True, null=True)
    address_zip = models.CharField(max_length=20, db_column='building_address_zip', blank=True, null=True)

    @property
    def address(self):
        parts = [self.address_street, self.address_brgy, self.address_city]
        return ", ".join(p for p in parts if p)

    @property
    def grade_desc(self):
        """
        Return the verbose description (“Super Prime Grade A”, …)
        corresponding to self.grade (“SPA”, …).
        """
        from .models import BuildingGrade  # local-scope import avoids circular ref
        row = BuildingGrade.objects.filter(code=self.grade).first()
        return row.description if row else None

    # ---------- meta ----------
    class Meta:
        db_table = 'pt_buildings'
        managed = False

    def __str__(self):
        return self.name


class BuildingGrade(models.Model):
    id = models.AutoField(primary_key=True, db_column='building_grade_id')
    code = models.CharField(max_length=3, db_column='building_grade')
    description = models.CharField(max_length=100, db_column='building_grade_desc')

    class Meta:
        db_table = 'pt_building_grades'
        managed = False
        verbose_name = 'building grade'

    def __str__(self):
        return f'{self.code} - {self.description}'


class BuildingType(models.Model):
    id = models.AutoField(primary_key=True, db_column='type_id')
    description = models.CharField(max_length=50)

    class Meta:
        db_table = 'pt_building_types'
        managed = False

    def __str__(self):
        return self.description


class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_column='unit_id')

    # ---------- identification ----------
    name = models.CharField(max_length=255, db_column='unit_name')
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE,
        related_name='units', db_column='building_id'
    )
    floor = BlankZeroIntegerField(
        db_column='unit_address_level', null=True, blank=True
    )  # e.g. 5, “LG”, etc.

    # ---------- marketing / occupancy ----------
    MARKETING_STATUS_CHOICES = [
        ('lease', 'For Lease'),
        ('sale', 'For Sale'),
        ('lease_sale', 'For Lease & Sale'),
        ('unknown', 'Don’t know'),
    ]
    marketing_status = models.CharField(
        max_length=20, choices=MARKETING_STATUS_CHOICES, default='unknown',
        db_column='unit_mktg_status'
    )

    VACANCY_STATUS_CHOICES = [('vacant', 'Vacant'), ('occupied', 'Occupied')]
    vacancy_status = models.CharField(
        max_length=20, choices=VACANCY_STATUS_CHOICES, default='vacant',
        db_column='unit_vacancy'
    )

    foreclosed = models.BooleanField(db_column='unit_foreclosed', default=False)

    # the legacy file stores “contact person / company” in a single varchar
    contact = models.CharField(
        max_length=255, db_column='unit_contact', blank=True, null=True
    )

    # ---------- sizes ----------
    gross_floor_area = BlankZeroDecimalField(
        max_digits=12, decimal_places=2, db_column='unit_gfa',
        null=True, blank=True
    )
    net_floor_area = BlankZeroDecimalField(
        max_digits=12, decimal_places=2, db_column='unit_nfa',
        null=True, blank=True
    )
    floor_to_ceiling_height = BlankZeroDecimalField(
        max_digits=6, decimal_places=2, db_column='unit_f2ch',
        null=True, blank=True
    )

    # ---------- fit-out ----------
    ceiling_condition = models.CharField(max_length=100, db_column='unit_ceiling_ho')
    floor_condition = models.CharField(max_length=100, db_column='unit_floor_ho')
    partition_condition = models.CharField(max_length=100, db_column='unit_partition_ho')

    # ---------- lease specifics ----------
    lease_commencement_date = models.DateField(
        null=True, blank=True, db_column='unit_lease_start'
    )
    lease_expiry_date = models.DateField(
        null=True, blank=True, db_column='unit_lease_end'
    )

    asking_rent = BlankZeroDecimalField(
        max_digits=12, decimal_places=2, db_column='unit_office_rent',
        null=True, blank=True
    )
    allocated_parking_slot = BlankZeroIntegerField(
        db_column='unit_alloc_parking_slot', null=True, blank=True
    )
    price_per_parking_slot = BlankZeroDecimalField(
        max_digits=12, decimal_places=2, db_column='unit_parking_rent',
        null=True, blank=True
    )
    minimum_period = models.CharField(
        max_length=50, db_column='unit_min_period', blank=True, null=True
    )
    escalation_rate = BlankZeroDecimalField(
        max_digits=6, decimal_places=2, db_column='unit_escalation_rate',
        null=True, blank=True
    )
    rent_free = models.CharField(
        max_length=50, db_column='unit_rent_free', blank=True, null=True
    )

    dues = BlankZeroDecimalField(
        max_digits=12, decimal_places=2, db_column='unit_dues',
        null=True, blank=True
    )

    # ---------- sale ----------
    sale_price_office = BlankZeroDecimalField(
        max_digits=14, decimal_places=2, db_column='unit_sale_price_office',
        null=True, blank=True
    )
    sale_price_parking = BlankZeroDecimalField(
        max_digits=14, decimal_places=2, db_column='unit_sale_price_parking',
        null=True, blank=True
    )

    # ---------- misc ----------
    notes = models.TextField(db_column='unit_notes', blank=True, null=True)

    contacts = models.ManyToManyField(
        Contact, blank=True, related_name='units', db_table='pt_unit_contacts'
    )

    # ---------- meta ----------
    class Meta:
        db_table = 'pt_units'
        managed = False

    # ---------- validation helpers ----------
    def clean(self):
        if (
                self.net_floor_area and self.gross_floor_area
                and self.net_floor_area > self.gross_floor_area
        ):
            raise ValidationError("Net floor area cannot exceed gross floor area")

        if (
                self.lease_commencement_date
                and self.lease_expiry_date
                and self.lease_commencement_date > self.lease_expiry_date
        ):
            raise ValidationError("Lease commencement must be before lease expiry")

    def __str__(self):
        return f"{self.name} ({self.building.name})"


class Company(models.Model):
    id = models.AutoField(primary_key=True, db_column='company_id')
    name = models.CharField(max_length=255, db_column='company_name')

    # ────────── address is stored flat in this table ──────────
    address_bldg = models.CharField(max_length=255, db_column='company_address_bldg', blank=True, null=True)
    address_street = models.CharField(max_length=255, db_column='company_address_street', blank=True, null=True)
    address_brgy = models.CharField(max_length=100, db_column='company_address_brgy', blank=True, null=True)
    address_city = models.CharField(max_length=100, db_column='company_address_city', blank=True, null=True)

    # other attributes
    industry = models.CharField(max_length=100, db_column='company_industry', blank=True, null=True)

    # OPTIONAL bookkeeping columns (keep only if the table really has them)
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, db_column='created_user_id',
        related_name='+', blank=True, null=True
    )
    created_at = models.DateTimeField(db_column='created_date', blank=True, null=True, auto_now_add=True)
    edited_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, db_column='edited_user_id',
        related_name='+', blank=True, null=True
    )
    edited_at = models.DateTimeField(db_column='edited_date', blank=True, null=True, auto_now=True)

    # meta
    class Meta:
        db_table = 'pt_companies'
        managed = False

    @property
    def full_address(self):
        parts = [self.address_bldg, self.address_street,
                 self.address_brgy, self.address_city]
        return ', '.join([p for p in parts if p])

    def __str__(self):
        return self.name


class ODForm(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column='od_form_id'
    )
    # the timestamp when the form was created
    created = MyDateTimeField(
        db_column='od_form_created',
        help_text='When this OD form was created'
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='od_forms',
        db_column='contact_id'
    )
    call_taken_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='od_form_call_taken'
    )
    TYPE_OF_CALL_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    type_of_call = models.CharField(
        max_length=10,
        choices=TYPE_OF_CALL_CHOICES,
        db_column='od_form_call_type'
    )
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
    source_of_call = models.CharField(
        max_length=20,
        choices=SOURCE_OF_CALL_CHOICES,
        db_column='od_form_call_source'
    )
    TYPE_OF_CALLER_CHOICES = [
        ('broker', 'Broker'),
        ('direct', 'Direct Buyer / Lease'),
    ]
    type_of_caller = models.CharField(
        max_length=20,
        choices=TYPE_OF_CALLER_CHOICES,
        db_column='od_form_caller_type'
    )
    INTENT_CHOICES = [
        ('rent', 'To Rent'),
        ('buy', 'To Buy'),
        ('both', 'Both'),
    ]
    intent = models.CharField(
        max_length=10,
        choices=INTENT_CHOICES,
        db_column='od_form_intent'
    )
    PURPOSE_CHOICES = [
        ('expanding', 'Expanding'),
        ('relocating', 'Relocating'),
        ('new_office', 'New Office'),
        ('consolidating', 'Consolidating'),
        ('downsizing', 'Downsizing'),
        ('upgrading', 'Upgrading'),
        ('expanding_retaining', 'Expanding while retaining'),
        ('others', 'Others'),
    ]
    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        db_column='od_form_purpose'
    )
    size_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='od_form_size_min',
        null=True, blank=True
    )
    size_maximum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='od_form_size_max',
        null=True, blank=True
    )
    budget_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='od_form_budget_min',
        null=True, blank=True
    )
    budget_maximum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='od_form_budget_max',
        null=True, blank=True
    )
    preferred_location = models.CharField(
        max_length=100,
        db_column='od_form_preferred_loc',
        null=True, blank=True
    )
    started_scouting = models.BooleanField(
        default=False,
        db_column='od_form_scouted',
        null=True, blank=True
    )
    notes = models.TextField(
        blank=True,
        null=True,
        db_column='od_form_notes'
    )
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('done_deal', 'Done Deal'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        db_column='od_form_status'
    )
    # who the form is assigned to / created for
    account_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='od_forms',
        db_column='user_id'
    )
    # track who created/edited the record
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='od_forms_created',
        db_column='created_user_id'
    )
    created_date = MyDateTimeField(
        auto_now_add=True,
        db_column='created_date'
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='od_forms_edited',
        db_column='edited_user_id'
    )
    edited_date = MyDateTimeField(
        auto_now=True,
        db_column='edited_date'
    )

    class Meta:
        db_table = 'pt_od_forms'
        managed = False

    def clean(self):
        if self.size_minimum > self.size_maximum:
            raise ValidationError(_('Size minimum cannot exceed size maximum'))
        if self.budget_minimum > self.budget_maximum:
            raise ValidationError(_('Budget minimum cannot exceed budget maximum'))

    def __str__(self):
        return f"OD Form {self.id} – {self.contact}"


class Note(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField(db_column='note_text')
    created_at = models.DateTimeField(db_column='created_at')

    class Meta:
        db_table = 'pt_notes'
        managed = False


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


class Image(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to='images/', validators=[validated_image_size])

    class Meta:
        db_table = 'pt_images'
        managed = False
