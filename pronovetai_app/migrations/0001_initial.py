# Generated by Django 5.1.7 on 2025-03-29 02:43

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("manager", "Manager"),
                            ("user", "User"),
                        ],
                        default="user",
                        help_text="Designated role: admin, manager or user",
                        max_length=20,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Building",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255)),
                ("year_built", models.PositiveIntegerField()),
                ("for_sale", models.BooleanField(default=False)),
                ("peza_certified", models.BooleanField(default=False)),
                ("is_strata", models.BooleanField(default=False)),
                ("grade", models.CharField(max_length=50)),
                (
                    "typical_floor_plate_area",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "floor_to_ceiling_height",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                ("number_of_floors", models.PositiveIntegerField()),
                ("parking_floors", models.PositiveIntegerField()),
                ("passenger_elevators", models.PositiveIntegerField()),
                ("service_elevators", models.PositiveIntegerField()),
                ("ac_type", models.CharField(max_length=50)),
                (
                    "ac_operating_hours_charge",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("office_rent", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "association_dues",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "floor_area_ratio",
                    models.DecimalField(decimal_places=2, max_digits=4),
                ),
                (
                    "gross_floor_area",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "gross_leasable_area",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("building_type", models.CharField(max_length=50)),
                (
                    "space_for_lease",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "space_for_sale",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "space_occupied",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_edited", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="buildings_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("street_address", models.CharField(max_length=255)),
                ("barangay", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=100)),
                ("industry", models.CharField(max_length=100)),
                ("contact", models.CharField(max_length=255)),
                (
                    "building",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="companies",
                        to="pronovetai_app.building",
                    ),
                ),
                (
                    "building_affiliations",
                    models.ManyToManyField(
                        blank=True,
                        related_name="affiliated_companies",
                        to="pronovetai_app.building",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=100, null=True)),
                ("first_name", models.CharField(blank=True, max_length=100, null=True)),
                ("last_name", models.CharField(blank=True, max_length=100, null=True)),
                ("email", models.EmailField(max_length=254)),
                ("position", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "mobile_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("fax_number", models.CharField(blank=True, max_length=20, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contacts",
                        to="pronovetai_app.company",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ODForm",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField()),
                (
                    "call_taken_by",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "type_of_call",
                    models.CharField(
                        choices=[("inbound", "Inbound"), ("outbound", "Outbound")],
                        max_length=10,
                    ),
                ),
                (
                    "source_of_call",
                    models.CharField(
                        choices=[
                            ("newspaper", "Newspaper"),
                            ("old_client", "Old Client"),
                            ("online_marketing", "Online Marketing"),
                            ("referral", "Referral"),
                            ("signage", "Signage"),
                            ("website", "Website"),
                            ("yellow_pages", "Yellow Pages"),
                            ("others", "Others"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "type_of_caller",
                    models.CharField(
                        choices=[
                            ("broker", "Broker"),
                            ("direct", "Direct Buyer / Lease"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "intent",
                    models.CharField(
                        choices=[
                            ("rent", "To Rent"),
                            ("buy", "To Buy"),
                            ("both", "Both"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "purpose",
                    models.CharField(
                        choices=[
                            ("expanding", "Expanding"),
                            ("relocating", "Relocating"),
                            ("new_office", "New Office"),
                            ("consolidating", "Consolidating"),
                            ("downsizing", "Downsizing"),
                            ("upgrading", "Upgrading"),
                            (
                                "expanding_retaining",
                                "Expanding while retaining current office",
                            ),
                            ("others", "Others"),
                        ],
                        max_length=30,
                    ),
                ),
                ("size_minimum", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "budget_minimum",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("prefered_location", models.CharField(max_length=100)),
                ("size_maximum", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "budget_maximum",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("started_scouting", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                            ("done_deal", "Done Deal"),
                        ],
                        default="active",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
                (
                    "account_manager",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"is_staff": True},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="od_forms",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="od_forms",
                        to="pronovetai_app.contact",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Unit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("floor", models.IntegerField()),
                (
                    "marketing_status",
                    models.CharField(
                        choices=[
                            ("lease", "For Lease"),
                            ("sale", "For Sale"),
                            ("lease_sale", "For Lease and For Sale"),
                            ("unknown", "Don't know"),
                        ],
                        default="unknown",
                        max_length=20,
                    ),
                ),
                (
                    "vacancy_status",
                    models.CharField(
                        choices=[("vacant", "Vacant"), ("occupied", "Occupied")],
                        default="vacant",
                        max_length=20,
                    ),
                ),
                ("foreclosed", models.BooleanField(default=False)),
                ("contact_information", models.CharField(max_length=255)),
                (
                    "gross_floor_area",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "net_floor_area",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "floor_to_ceiling_height",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                ("ceiling_condition", models.CharField(max_length=100)),
                ("floor_condition", models.CharField(max_length=100)),
                ("partition_condition", models.CharField(max_length=100)),
                ("lease_commencement_date", models.DateField(blank=True, null=True)),
                ("lease_expiry_date", models.DateField(blank=True, null=True)),
                (
                    "asking_rent",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "allocated_parking_slot",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "price_per_parking_slot",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "minimum_period",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "escalation_rate",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=4, null=True
                    ),
                ),
                ("rent_free", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "dues",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "sale_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "sale_parking",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("unit_notes", models.TextField(blank=True, null=True)),
                (
                    "building",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="units",
                        to="pronovetai_app.building",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="company",
            name="unit_affiliations",
            field=models.ManyToManyField(
                blank=True,
                related_name="affiliated_companies",
                to="pronovetai_app.unit",
            ),
        ),
    ]
