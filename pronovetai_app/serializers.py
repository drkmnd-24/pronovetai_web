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
        fields = '__all__'


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
    address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        model = Company
        fields = '__all__'

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            addr = Address.objects.create(**address_data)
            validated_data['address'] = addr
        return Company.objects.create(**validated_data)

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            if instance.address:
                for k, v in address_data.items():
                    setattr(instance.address, k, v)
                instance.address.save()
            else:
                instance.address = Address.objects.create(**address_data)
        return super().update(instance, validated_data)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True)  # uses the @property above

    class Meta:
        model = Building
        fields = [
            'id', 'name', 'grade', 'building_type',
            'is_peza_certified', 'is_strata',
            'year_built', 'address'
        ]

    def update(self, instance, validated_data):
        addr_data = validated_data.pop('address', None)
        if addr_data:
            if instance.address:
                for k, v in addr_data.items():
                    setattr(instance.address, k, v)
                instance.address.save()
            else:
                instance.address = Address.objects.create(**addr_data)
        return super().update(instance, validated_data)


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

    def validate(self, data):
        # trigger model.clean()
        Unit(**data).clean()
        return data


class ODFormSerializer(serializers.ModelSerializer):
    ize_minimum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    size_maximum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    budget_minimum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    budget_maximum = NullableDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = ODForm
        fields = '__all__'

    def validate(self, data):
        ODForm(**data).clean()
        return data


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
