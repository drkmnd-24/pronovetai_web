from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import password_validation

from .models import (
    UserType,
    User,
    UserLog,
    Address,
    Company,
    Contact,
    Building,
    BuildingType,
    BuildingImage,
    Unit,
    ODForm,
    UnitImage,
)
from decimal import InvalidOperation


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
class NullableDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        if value in (None, ""):
            return None
        try:
            return super().to_representation(value)
        except InvalidOperation:
            return None


# -----------------------------------------------------------------------------
# Users
# -----------------------------------------------------------------------------
class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ["id", "description"]


class StaffRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "user_type",  # id or label supported by manager
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        creator = self.context["request"].user
        return User.objects.create_user(created_by=creator, **validated_data)


class ManagerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "user_type",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        creator = self.context["request"].user
        return User.objects.create_user(is_staff=True, created_by=creator, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined", "user_type"]


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = ["id", "message", "timestamp"]


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


# -----------------------------------------------------------------------------
# Companies / Contacts
# -----------------------------------------------------------------------------
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["street_address", "barangay", "city"]


class CompanySerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "industry",
            "address_bldg",
            "address_street",
            "address_brgy",
            "address_city",
            "full_address",
        ]
        extra_kwargs = {
            "industry": {"required": False, "allow_null": True},
            "address_bldg": {"required": False, "allow_null": True},
            "address_street": {"required": False, "allow_null": True},
            "address_brgy": {"required": False, "allow_null": True},
            "address_city": {"required": False, "allow_null": True},
        }

    def _add_bookkeeping(self, validated, *, is_update=False):
        user = self.context["request"].user
        names = {f.name for f in Company._meta.fields}
        if "created_by" in names and not is_update:
            validated.setdefault("created_by", user)
        if "edited_by" in names:
            validated.setdefault("edited_by", user)
        if "created_at" in names and not is_update:
            validated.setdefault("created_at", timezone.now())
        if "edited_at" in names:
            validated.setdefault("edited_at", timezone.now())
        return validated

    def create(self, validated):
        return super().create(self._add_bookkeeping(validated, is_update=False))

    def update(self, instance, validated):
        return super().update(instance, self._add_bookkeeping(validated, is_update=True))


class ContactSerializer(serializers.ModelSerializer):
    contact_title = serializers.CharField(source="title", required=False, allow_blank=True)
    contact_position = serializers.CharField(source="position", required=False, allow_blank=True)
    contact_email = serializers.EmailField(source="email", required=False, allow_blank=True)

    full_name = serializers.ReadOnlyField()
    company_name = serializers.CharField(source="company.name", read_only=True)

    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "contact_title",
            "first_name",
            "last_name",
            "full_name",
            "contact_position",
            "contact_email",
            "phone_number",
            "mobile_number",
            "fax_number",
            "notes",
            "company",
            "company_name",
        ]
        read_only_fields = ("full_name", "company_name")
        extra_kwargs = {
            "contact_position": {"required": False, "allow_blank": True},
            "contact_email": {"required": False, "allow_blank": True},
            "phone_number": {"required": False, "allow_blank": True},
            "mobile_number": {"required": False, "allow_blank": True},
            "fax_number": {"required": False, "allow_blank": True},
            "notes": {"required": False, "allow_blank": True},
        }


# -----------------------------------------------------------------------------
# Buildings (note: building_type is varchar on the building; we expose description)
# -----------------------------------------------------------------------------
class BuildingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingImage
        fields = "__all__"


class BuildingSerializer(serializers.ModelSerializer):
    grade_desc = serializers.ReadOnlyField()
    building_type_desc = serializers.SerializerMethodField()

    # Image helpers: allow upload to pt_building_images and expose a URL back
    main_image = serializers.ImageField(write_only=True, required=False)
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = [
            "id",
            "name",
            "marketing_status",
            "grade",
            "grade_desc",
            "building_type",
            "building_type_desc",
            "peza",
            "strata",
            "year_built",
            "address_street",
            "address_brgy",
            "address_city",
            "address_zip",
            "total_levels",
            "plate_area",
            "f2ch",
            "parking_count",
            "parking_level",
            "pass_lift",
            "service_lift",
            "ac_type",
            "ac_op_hours",
            "ac_ext_hours",
            "ac_op_charge",
            "ac_ext_charge",
            "ps_backup",
            "ps_desc",
            "notes",
            "sale_price_php",
            "lot_area",
            "far",
            "gfa",
            "gla",
            "office_rent",
            "rent_1",
            "rent_2",
            "assoc_dues",
            # image helpers
            "main_image",
            "main_image_url",
        ]

    def get_building_type_desc(self, obj):
        row = BuildingType.objects.filter(code=obj.building_type).first()
        return row.description if row else None

    def get_main_image_url(self, obj):
        img = obj.images.order_by("id").first()
        return img.image.url if img and getattr(img.image, "url", None) else None

    def create(self, validated_data):
        image = validated_data.pop("main_image", None)
        building = super().create(validated_data)
        if image:
            BuildingImage.objects.create(building=building, image=image)
        return building

    def update(self, instance, validated_data):
        image = validated_data.pop("main_image", None)
        building = super().update(instance, validated_data)
        if image:
            BuildingImage.objects.create(building=building, image=image)
        return building


# -----------------------------------------------------------------------------
# Units & OD Forms
# -----------------------------------------------------------------------------
class UnitSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = Unit
        fields = (
            "id",
            "name",
            "building",
            "building_name",
            "floor",
            "marketing_status",
            "vacancy_status",
            "foreclosed",
            "gross_floor_area",
            "net_floor_area",
            "floor_to_ceiling_height",
            "lease_commencement_date",
            "lease_expiry_date",
            "asking_rent",
            "allocated_parking_slot",
            "price_per_parking_slot",
            "minimum_period",
            "escalation_rate",
            "rent_free",
            "dues",
            "sale_price_office",
            "sale_price_parking",
            "notes",
        )


class ODFormSerializer(serializers.ModelSerializer):
    size_minimum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    size_maximum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    budget_minimum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    budget_maximum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = ODForm
        fields = "__all__"
        read_only_fields = ("account_manager", "created_by", "created_date", "edited_by", "edited_date")

    def validate(self, data):
        # Use model.clean for cross-field rules
        ODForm(**data).clean()
        return data


class UnitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitImage
        fields = "__all__"
