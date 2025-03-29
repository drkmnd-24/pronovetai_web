from rest_framework import serializers
from .models import Building, Unit, Company


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class UnitSerializer(serializers.ModelSerializer):
    building = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())

    class Meta:
        model = Unit
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    building = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())
    building_affiliations = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all(), many=True,
                                                               required=False)
    unit_affiliations = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), many=True, required=False)

    class Meta:
        model = Company
        fields = '__all__'
