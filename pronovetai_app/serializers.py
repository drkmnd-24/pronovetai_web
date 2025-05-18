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


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'description']


class StaffRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        # we no longer have a 'role' field; we'll hard‐code user_type
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # pick the UserType row whose description is “User”
        user_type = UserType.objects.get(description__iexact='User')
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=user_type,
        )
        user.set_password(validated_data['password'])
        # no DB column, but Django/auth will read this flag in memory:
        user.is_staff = False
        user.save()
        return user


class ManagerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user_type = UserType.objects.get(description__iexact='Manager')
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=user_type,
        )
        user.set_password(validated_data['password'])
        user.is_staff = True
        user.save()
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
    address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        model = Building
        fields = '__all__'

    def create(self, validated_data):
        addr_data = validated_data.pop('address', None)
        if addr_data:
            addr = Address.objects.create(**addr_data)
            validated_data['address'] = addr
        return Building.objects.create(**validated_data)

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
    class Meta:
        model = ODForm
        fields = '__all__'

    def validate(self, data):
        ODForm(**data).clean()
        return data


class BuildingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingImage
        fields = '__all__'


class UnitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitImage
        fields = '__all__'
