from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .fields import BlankZeroIntegerField, BlankZeroDecimalField


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
class MyDateTimeField(models.DateTimeField):
    """Parse MySQL DATETIME strings and treat '0000-00-00...' as None."""

    def get_db_converters(self, connection):
        return [self.from_db_value]

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, str) and value.startswith("0000-00-00"):
            return None
        if isinstance(value, str):
            dt = parse_datetime(value)
            if dt is None:
                return super().to_python(value)
            if settings.USE_TZ:
                tz = getattr(connection, "timezone", timezone.get_current_timezone())
                dt = timezone.make_aware(dt, tz)
            return dt
        return value

    def to_python(self, value):
        if isinstance(value, str) and value.startswith("0000-00-00"):
            return None
        return super().to_python(value)


def validated_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("Maximum file size allowed is 5MB")


# -----------------------------------------------------------------------------
# Users
# -----------------------------------------------------------------------------
class UserType(models.Model):
    id = models.AutoField(primary_key=True, db_column="user_type_id")
    description = models.CharField(max_length=255, db_column="user_type_desc")
    created_at = models.DateTimeField(db_column="user_type_created")

    class Meta:
        db_table = "pt_user_types"
        managed = False

    def __str__(self) -> str:
        return self.description


class CustomUserManager(BaseUserManager):
    """Manager that keeps your legacy UserType flexible (id or label)."""

    def _require_user_type(self, extra: dict):
        val = extra.get("user_type")
        if isinstance(val, UserType):
            return

        # id as int/str
        if isinstance(val, (int, str)) and str(val).isdigit():
            try:
                extra["user_type"] = UserType.objects.get(pk=int(val))
                return
            except ObjectDoesNotExist:
                raise ValueError(f"UserType id={val} does not exist")

        # label
        if isinstance(val, str):
            obj = UserType.objects.filter(description__iexact=val).first()
            if obj:
                extra["user_type"] = obj
                return

        default = UserType.objects.first()
        if default:
            extra["user_type"] = default
        else:
            raise ValueError(
                "Please create at least one UserType row or pass a valid user_type."
            )

    def create_user(self, username, password=None, created_by=None, **extra):
        if not username:
            raise ValueError("Username must be set")
        self._require_user_type(extra)
        extra.setdefault("date_joined", timezone.now())
        user = self.model(username=username, created_by=created_by, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        self._require_user_type(extra)
        return self.create_user(username, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, db_column="user_id")
    username = models.CharField(max_length=150, unique=True, db_column="user_login")
    password = models.CharField(max_length=128, db_column="user_pass")
    email = models.EmailField(db_column="user_email", blank=True)
    first_name = models.CharField(max_length=150, db_column="user_first_name", blank=True)
    last_name = models.CharField(max_length=150, db_column="user_last_name", blank=True)

    last_login = MyDateTimeField(db_column="last_login", null=True, blank=True)
    date_joined = MyDateTimeField(db_column="user_registered", default=timezone.now)

    created_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="created_user_id", related_name="users_created"
    )
    created_date = MyDateTimeField(db_column="created_date", auto_now_add=True)
    edited_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="edited_user_id", related_name="users_edited"
    )
    edited_date = MyDateTimeField(db_column="edited_date", auto_now=True)

    user_type = models.ForeignKey(
        UserType, verbose_name="User type (ID or label)",
        on_delete=models.SET_NULL, null=True, db_column="user_type_id", related_name="users"
    )

    is_active = models.BooleanField(default=True, db_column="is_active")
    is_staff = models.BooleanField(default=False, db_column="is_staff")

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "user_type"]

    class Meta:
        db_table = "pt_users"
        managed = False

    def __str__(self) -> str:
        return self.username


class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs", db_column="user_id")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pt_user_logs"
        managed = False

    def __str__(self) -> str:
        return f"Log for {self.user.username} at {self.timestamp}"


# -----------------------------------------------------------------------------
# Companies / Contacts
# -----------------------------------------------------------------------------
class Address(models.Model):
    street_address = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)

    class Meta:
        db_table = "pt_addresses"
        managed = False

    def __str__(self) -> str:
        return f"{self.street_address or ''} - {self.city}"


class Company(models.Model):
    id = models.AutoField(primary_key=True, db_column="company_id")
    name = models.CharField(max_length=255, db_column="company_name")

    address_bldg = models.CharField(max_length=255, db_column="company_address_bldg", blank=True, null=True)
    address_street = models.CharField(max_length=255, db_column="company_address_street", blank=True, null=True)
    address_brgy = models.CharField(max_length=100, db_column="company_address_brgy", blank=True, null=True)
    address_city = models.CharField(max_length=100, db_column="company_address_city", blank=True, null=True)

    industry = models.CharField(max_length=100, db_column="company_industry", blank=True, null=True)

    # Bookkeeping (legacy columns exist in many tables; keep nullable to be safe)
    created_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, db_column="created_user_id",
        related_name="+", blank=True, null=True
    )
    created_at = models.DateTimeField(db_column="created_date", blank=True, null=True, auto_now_add=True)
    edited_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, db_column="edited_user_id",
        related_name="+", blank=True, null=True
    )
    edited_at = models.DateTimeField(db_column="edited_date", blank=True, null=True, auto_now=True)

    class Meta:
        db_table = "pt_companies"
        managed = False

    @property
    def full_address(self) -> str:
        parts = [self.address_bldg, self.address_street, self.address_brgy, self.address_city]
        return ", ".join([p for p in parts if p])

    def __str__(self) -> str:
        return self.name


class Contact(models.Model):
    id = models.AutoField(primary_key=True, db_column="contact_id")

    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, db_column="company_id", related_name="contacts"
    )

    # personal info
    title = models.CharField(max_length=100, db_column="contact_title", blank=True, null=True)
    first_name = models.CharField(max_length=100, db_column="contact_first_name", blank=True, null=True)
    last_name = models.CharField(max_length=100, db_column="contact_last_name", blank=True, null=True)
    files_as = models.CharField(max_length=255, db_column="contact_files_as", blank=True, null=True)
    position = models.CharField(max_length=100, db_column="contact_position", blank=True, null=True)

    # comms
    phone_number = models.CharField(max_length=20, db_column="contact_phone", blank=True, null=True)
    mobile_number = models.CharField(max_length=20, db_column="contact_mobile", blank=True, null=True)
    fax_number = models.CharField(max_length=20, db_column="contact_fax", blank=True, null=True)
    email = models.CharField(max_length=254, db_column="contact_email", blank=True, null=True)

    notes = models.TextField(db_column="contact_notes", blank=True, null=True)

    class Meta:
        db_table = "pt_contacts"
        managed = False

    @property
    def full_name(self) -> str | None:
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or None

    def __str__(self) -> str:
        return self.full_name or self.email or str(self.id)


# -----------------------------------------------------------------------------
# Buildings & Units (fixes: correct building type table/columns; no FK on varchar)
# -----------------------------------------------------------------------------
class BuildingGrade(models.Model):
    id = models.AutoField(primary_key=True, db_column="building_grade_id")
    code = models.CharField(max_length=20, db_column="building_grade")
    description = models.CharField(max_length=255, db_column="building_grade_desc")

    class Meta:
        db_table = "pt_building_grades"
        managed = False
        verbose_name = "building grade"

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"


class BuildingType(models.Model):
    """Matches pt_building_types exactly (fix wrong column names)."""

    id = models.AutoField(primary_key=True, db_column="building_type_id")
    code = models.CharField(max_length=20, db_column="building_type")
    description = models.CharField(max_length=255, db_column="building_type_desc")

    class Meta:
        db_table = "pt_building_types"
        managed = False

    def __str__(self) -> str:
        return self.description


class Building(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="building_id")

    # basic facts
    name = models.CharField(max_length=255, db_column="building_name")
    marketing_status = models.CharField(max_length=50, db_column="building_mktg_status")

    # grade is a plain varchar in pt_buildings – keep as-is, expose a helper to read description
    grade = models.CharField(max_length=50, db_column="building_grade", blank=True, null=True)

    # building_type is a varchar in pt_buildings – **do not** declare FK (would join int↔varchar)
    building_type = models.CharField(max_length=50, db_column="building_type", blank=True, null=True)

    peza = models.CharField(max_length=50, db_column="building_peza")
    strata = models.CharField(max_length=20, db_column="building_strata")
    year_built = models.CharField(max_length=20, db_column="building_year_built")

    contact_blob = models.CharField(max_length=1000, db_column="building_contact")

    # address
    address_street = models.CharField(max_length=100, db_column="building_address_street")
    address_brgy = models.CharField(max_length=100, db_column="building_address_brgy")
    address_city = models.CharField(max_length=100, db_column="building_address_city")
    address_zip = models.CharField(max_length=10, db_column="building_address_zip")

    # numbers / sizes (legacy stores many numeric values in varchar – keep tolerant decimal fields)
    total_levels = BlankZeroIntegerField(db_column="building_total_level", null=True, blank=True)
    plate_area = BlankZeroDecimalField(max_digits=12, decimal_places=2, db_column="building_plate_area", null=True,
                                       blank=True)
    f2ch = BlankZeroDecimalField(max_digits=6, decimal_places=2, db_column="building_f2ch", null=True, blank=True)
    parking_count = models.CharField(max_length=255, db_column="building_parking_count")
    parking_level = models.CharField(max_length=255, db_column="building_parking_level")

    pass_lift = models.CharField(max_length=10, db_column="building_pass_lift")
    service_lift = models.CharField(max_length=10, db_column="building_service_lift")

    ac_type = models.CharField(max_length=255, db_column="building_ac_type")
    ac_op_hours = models.CharField(max_length=255, db_column="building_ac_ophrs")
    ac_ext_hours = models.CharField(max_length=255, db_column="building_ac_exthrs")
    ac_op_charge = models.CharField(max_length=255, db_column="building_ac_ophrs_chg")
    ac_ext_charge = models.CharField(max_length=255, db_column="building_ac_exthrs_chg")

    ps_backup = models.CharField(max_length=20, db_column="building_ps_backup")
    ps_desc = models.TextField(db_column="building_ps_desc")

    notes = models.TextField(db_column="building_notes")

    sale_price_php = models.CharField(max_length=50, db_column="building_sale_php")
    lot_area = models.CharField(max_length=50, db_column="building_lot_area")
    far = models.CharField(max_length=50, db_column="building_far")
    gfa = BlankZeroDecimalField(max_digits=14, decimal_places=2, db_column="building_gfa", null=True, blank=True)
    gla = BlankZeroDecimalField(max_digits=14, decimal_places=2, db_column="building_gla", null=True, blank=True)

    office_rent = models.CharField(max_length=50, db_column="building_office_rent")
    rent_1 = models.CharField(max_length=50, db_column="building_1rent")
    rent_2 = models.CharField(max_length=50, db_column="building_2rent")
    assoc_dues = models.CharField(max_length=255, db_column="building_assoc_dues")

    # convenience: not stored in pt_buildings; upload stored in pt_building_images (see BuildingImage below)
    # We expose a computed "main image" via serializer; no DB column added here (managed=False)

    class Meta:
        db_table = "pt_buildings"
        managed = False

    def __str__(self) -> str:
        return self.name

    @property
    def address(self) -> str:
        parts = [self.address_street, self.address_brgy, self.address_city]
        return ", ".join([p for p in parts if p])

    @property
    def grade_desc(self) -> str | None:
        row = BuildingGrade.objects.filter(code=self.grade).first()
        return row.description if row else None

    @property
    def building_type_desc(self) -> str | None:
        row = BuildingType.objects.filter(code=self.building_type).first()
        return row.description if row else None


class BuildingLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='logs', db_column='building_id'
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', db_column='user_id'
    )
    message = models.TextField()
    timestamp = MyDateTimeField(db_column='timestamp', default=timezone.now)

    class Meta:
        db_table = 'pt_building_logs'
        managed = False
        ordering = ['-timestamp']

    def __str__(self):
        who = (self.user.get_full_name() or self.user.username) if self.user else 'Someone'
        return f'[{self.timestamp}] {who}: {self.message[:40]}'


class Unit(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="unit_id")

    name = models.CharField(max_length=255, db_column="unit_name")
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="units", db_column="building_id"
    )

    floor = models.CharField(max_length=10, db_column="unit_address_level")
    contact = models.CharField(max_length=1000, db_column="unit_contact")

    gross_floor_area = BlankZeroDecimalField(max_digits=12, decimal_places=2, db_column="unit_gfa", null=True,
                                             blank=True)
    net_floor_area = BlankZeroDecimalField(max_digits=12, decimal_places=2, db_column="unit_nfa", null=True, blank=True)
    floor_to_ceiling_height = BlankZeroDecimalField(max_digits=6, decimal_places=2, db_column="unit_f2ch", null=True,
                                                    blank=True)

    marketing_status = models.CharField(max_length=50, db_column="unit_mktg_status")
    vacancy_status = models.CharField(max_length=50, db_column="unit_vacancy")
    foreclosed = models.CharField(max_length=50, db_column="unit_foreclosed")

    ceiling_condition = models.CharField(max_length=500, db_column="unit_ceiling_ho")
    floor_condition = models.CharField(max_length=500, db_column="unit_floor_ho")
    partition_condition = models.CharField(max_length=500, db_column="unit_partition_ho")

    lease_commencement_date = models.DateField(null=True, blank=True, db_column="unit_lease_start")
    lease_expiry_date = models.DateField(null=True, blank=True, db_column="unit_lease_end")

    asking_rent = models.CharField(max_length=50, db_column="unit_office_rent")
    allocated_parking_slot = BlankZeroIntegerField(db_column="unit_alloc_parking_slot", null=True, blank=True)
    price_per_parking_slot = models.CharField(max_length=50, db_column="unit_parking_rent")
    minimum_period = models.CharField(max_length=50, db_column="unit_min_period")
    escalation_rate = models.CharField(max_length=255, db_column="unit_escalation_rate")
    rent_free = models.CharField(max_length=255, db_column="unit_rent_free")
    dues = BlankZeroDecimalField(max_digits=12, decimal_places=2, db_column="unit_dues", null=True, blank=True)

    sale_price_office = models.CharField(max_length=50, db_column="unit_sale_price_office")
    sale_price_parking = models.CharField(max_length=50, db_column="unit_sale_price_parking")

    notes = models.TextField(db_column="unit_notes", blank=True, null=True)

    # Many-to-many to contacts via existing table
    contacts = models.ManyToManyField(Contact, blank=True, related_name="units", db_table="pt_unit_contacts")

    class Meta:
        db_table = "pt_units"
        managed = False

    def clean(self):
        if self.net_floor_area and self.gross_floor_area and self.net_floor_area > self.gross_floor_area:
            raise ValidationError("Net floor area cannot exceed gross floor area")
        if (
                self.lease_commencement_date
                and self.lease_expiry_date
                and self.lease_commencement_date > self.lease_expiry_date
        ):
            raise ValidationError("Lease commencement must be before lease expiry")

    def __str__(self) -> str:
        return f"{self.name} ({self.building.name})"


# -----------------------------------------------------------------------------
# OD Forms (unchanged except for safety)
# -----------------------------------------------------------------------------
class ODForm(models.Model):
    id = models.AutoField(primary_key=True, db_column="od_form_id")
    created = MyDateTimeField(db_column="od_form_created")

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="od_forms", db_column="contact_id"
    )
    call_taken_by = models.CharField(max_length=255, null=True, blank=True, db_column="od_form_call_taken")

    TYPE_OF_CALL_CHOICES = [("inbound", "Inbound"), ("outbound", "Outbound")]
    type_of_call = models.CharField(max_length=10, choices=TYPE_OF_CALL_CHOICES, db_column="od_form_call_type")

    SOURCE_OF_CALL_CHOICES = [
        ("newspaper", "Newspaper"),
        ("old_client", "Old Client"),
        ("online_marketing", "Online Marketing"),
        ("referral", "Referral"),
        ("signage", "Signage"),
        ("website", "Website"),
        ("yellow_pages", "Yellow Pages"),
        ("others", "Others"),
    ]
    source_of_call = models.CharField(max_length=20, choices=SOURCE_OF_CALL_CHOICES, db_column="od_form_call_source")

    TYPE_OF_CALLER_CHOICES = [("broker", "Broker"), ("direct", "Direct Buyer / Lease")]
    type_of_caller = models.CharField(max_length=20, choices=TYPE_OF_CALLER_CHOICES, db_column="od_form_caller_type")

    INTENT_CHOICES = [("rent", "To Rent"), ("buy", "To Buy"), ("both", "Both")]
    intent = models.CharField(max_length=10, choices=INTENT_CHOICES, db_column="od_form_intent")

    PURPOSE_CHOICES = [
        ("expanding", "Expanding"),
        ("relocating", "Relocating"),
        ("new_office", "New Office"),
        ("consolidating", "Consolidating"),
        ("downsizing", "Downsizing"),
        ("upgrading", "Upgrading"),
        ("expanding_retaining", "Expanding while retaining"),
        ("others", "Others"),
    ]
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, db_column="od_form_purpose")

    size_minimum = models.DecimalField(max_digits=10, decimal_places=2, db_column="od_form_size_min", null=True,
                                       blank=True)
    size_maximum = models.DecimalField(max_digits=10, decimal_places=2, db_column="od_form_size_max", null=True,
                                       blank=True)
    budget_minimum = models.DecimalField(max_digits=10, decimal_places=2, db_column="od_form_budget_min", null=True,
                                         blank=True)
    budget_maximum = models.DecimalField(max_digits=10, decimal_places=2, db_column="od_form_budget_max", null=True,
                                         blank=True)

    preferred_location = models.CharField(max_length=100, db_column="od_form_preferred_loc", null=True, blank=True)
    started_scouting = models.BooleanField(default=False, db_column="od_form_scouted", null=True, blank=True)
    notes = models.TextField(blank=True, null=True, db_column="od_form_notes")

    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive"), ("done_deal", "Done Deal")]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active", db_column="od_form_status")

    account_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="od_forms", db_column="user_id"
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="od_forms_created",
        db_column="created_user_id"
    )
    created_date = MyDateTimeField(auto_now_add=True, db_column="created_date")

    edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="od_forms_edited",
        db_column="edited_user_id"
    )
    edited_date = MyDateTimeField(auto_now=True, db_column="edited_date")

    class Meta:
        db_table = "pt_od_forms"
        managed = False

    def clean(self):
        if self.size_minimum and self.size_maximum and self.size_minimum > self.size_maximum:
            raise ValidationError("Size minimum cannot exceed size maximum")
        if self.budget_minimum and self.budget_maximum and self.budget_minimum > self.budget_maximum:
            raise ValidationError("Budget minimum cannot exceed budget maximum")

    def __str__(self) -> str:
        return f"OD Form {self.id} – {self.contact}"


# -----------------------------------------------------------------------------
# Generic notes/images + dedicated image tables
# -----------------------------------------------------------------------------
class Note(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField(db_column="note_text")
    created_at = models.DateTimeField(db_column="created_at")

    class Meta:
        db_table = "pt_notes"
        managed = False


class BuildingImage(models.Model):
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="images", db_column="building_id"
    )
    image = models.ImageField(upload_to="building_images/", validators=[validated_image_size])

    class Meta:
        db_table = "pt_building_images"
        managed = False

    def __str__(self) -> str:
        return f"Image for {self.building.name}"


class UnitImage(models.Model):
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="images", db_column="unit_id"
    )
    image = models.ImageField(upload_to="unit_images/", validators=[validated_image_size])

    class Meta:
        db_table = "pt_unit_images"
        managed = False

    def __str__(self) -> str:
        return f"Image for {self.unit.name}"


class Image(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    image = models.ImageField(upload_to="images/", validators=[validated_image_size])

    class Meta:
        db_table = "pt_images"
        managed = False
