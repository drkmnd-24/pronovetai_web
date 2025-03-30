from rest_framework import serializers
from .models import (Address, User, Company,
                     Contact, Building, Unit,
                     ODForm, BuildingImage, UnitImage)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class CompanySerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        model = Company
        fields = '__all__'

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            address = Address.objects.create(**address_data)
            validated_data['address'] = address
        return Company.objects.create(**validated_data)

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data and instance.address:
            address = instance.address
            for key, value in address_data.items():
                setattr(address, key, value)
            address.save()
        elif address_data:
            address = Address.objects.create(**address_data)
            instance.address = address
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
        address_data = validated_data.pop('address', None)
        if address_data:
            address = Address.objects.create(**address_data)
            validated_data['address'] = address
        return Building.objects.create(**validated_data)

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data and instance.address:
            address = instance.address
            for key, value in address_data.items():
                setattr(address, key, value)
            address.save()
        elif address_data:
            address = Address.objects.create(**address_data)
            instance.address = address
        return super().update(instance, validated_data)


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

    def validate(self, data):
        # Invoke model clean() for custom validations.
        instance = Unit(**data)
        instance.clean()
        return data


class ODFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ODForm
        fields = '__all__'

    def validate(self, data):
        # Invoke model clean() for custom validations.
        instance = ODForm(**data)
        instance.clean()
        return data


class BuildingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingImage
        fields = '__all__'


class UnitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitImage
        fields = '__all__'
