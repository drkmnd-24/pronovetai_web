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
    Unit,
    ODForm,
    BuildingImage,
    UnitImage,
)
from decimal import Decimal, InvalidOperation


class NullableDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        # catch None or empty‐string
        if value in (None, ""):
            return None
        try:
            return super().to_representation(value)
        except InvalidOperation:
            return None


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'description']


class StaffRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'confirm_password'
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        creator = self.context['request'].user
        # fetch the “User” user_type
        user_type = UserType.objects.get(description__iexact='User')
        # call through your manager, passing created_by
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=user_type,
            created_by=creator
        )
        return user


class ManagerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'confirm_password'
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        creator = self.context['request'].user
        manager_type = UserType.objects.get(description__iexact='Manager')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=manager_type,
            created_by=creator,
            is_staff=True
        )
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street_address', 'barangay',
                  'city', ]


class UserSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'user_type']


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = ['id', 'message', 'timestamp']


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class CompanySerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'industry',
            'address_bldg', 'address_street', 'address_brgy', 'address_city',
            'full_address',
        ]
        extra_kwargs = {
            # every column is optional in the API
            'industry': {'required': False, 'allow_null': True},
            'address_bldg': {'required': False, 'allow_null': True},
            'address_street': {'required': False, 'allow_null': True},
            'address_brgy': {'required': False, 'allow_null': True},
            'address_city': {'required': False, 'allow_null': True},
        }

    # ---------- bookkeeping helper ------------------
    def _add_bookkeeping(self, validated, *, is_update=False):
        user = self.context['request'].user
        names = {f.name for f in Company._meta.fields}

        if 'created_by' in names and not is_update:
            validated.setdefault('created_by', user)
        if 'edited_by' in names:
            validated.setdefault('edited_by', user)

        if 'created_at' in names and not is_update:
            validated.setdefault('created_at', timezone.now())
        if 'edited_at' in names:
            validated.setdefault('edited_at', timezone.now())
        return validated

    # ---------- create / update ----------------------
    def create(self, validated):
        validated = self._add_bookkeeping(validated, is_update=False)
        return super().create(validated)

    def update(self, instance, validated):
        validated = self._add_bookkeeping(validated, is_update=True)
        return super().update(instance, validated)


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    company_name = serializers.CharField(source='company.name', read_only=True)

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Contact
        fields = [
            'id', 'title', 'first_name', 'last_name', 'full_name',
            'position', 'email', 'phone_number', 'mobile_number',
            'fax_number', 'notes', 'company', 'company_name',
        ]
        read_only_fields = ['full_name', 'company_name']

    def get_contact_type(self, obj):
        # nothing in the table yet – leave the column blank
        return ''


class BuildingSerializer(serializers.ModelSerializer):
    # pull the *computed* property from the model
    grade_desc = serializers.ReadOnlyField()
    # plain code (“SPA”, …)
    grade = serializers.CharField()

    class Meta:
        model = Building
        fields = [
            "id", "name", "grade", "grade_desc",
            "is_peza_certified", "is_strata",
            "address_city",
        ]

    def create(self, validated_data):
        addr_data = validated_data.pop('address', None)
        building = super().create(validated_data)
        if addr_data:
            building.address = Address.objects.create(**addr_data)
            building.save()
        return building

    def update(self, instance, validated_data):
        addr_data = validated_data.pop('address', None)
        if addr_data:
            if instance.address_id:
                for k, v in addr_data.items():
                    setattr(instance.address, k, v)
                instance.address.save()
            else:
                instance.address = Address.objects.create(**addr_data)
        return super().update(instance, validated_data)


class UnitSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(
        source="building.name", read_only=True
    )
    marketing_status_display = serializers.SerializerMethodField()
    vacancy_status_display = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = (
            "id", "name", "building_name", "floor",
            "marketing_status", "marketing_status_display",
            "vacancy_status", "vacancy_status_display",
            "foreclosed",
        )

    def get_marketing_status_display(self, obj):
        return obj.get_marketing_status_display()

    def get_vacancy_status_display(self, obj):
        return obj.get_vacancy_status_display()


class ODFormSerializer(serializers.ModelSerializer):
    size_minimum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    size_maximum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    budget_minimum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    budget_maximum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = ODForm
        fields = '__all__'
        read_only_fields = (
            'account_manager', 'created_by', 'created_date',
            'edited_by', 'edited_date',  # ← here
        )

    def validate(self, data):
        ODForm(**data).clean()
        return data

    def validate_contact(self, value):
        if value is None:
            raise serializers.ValidationError('Select a contact (caller)')
        raise value


class NullableZeroDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        if value == 0:
            return None
        return super().to_representation(value)


class BuildingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingImage
        fields = '__all__'


class UnitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitImage
        fields = '__all__'
