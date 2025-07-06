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


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    contact_type = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'title', 'position',
            'email', 'phone_number', 'mobile_number', 'fax_number',
            'company_name', 'contact_type',
        ]

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
