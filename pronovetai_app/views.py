from rest_framework import viewsets
from .models import Address, User, Company, Contact, Building, Unit, ODForm
from .serializers import (
    AddressSerializer, UserSerializer, CompanySerializer, ContactSerializer,
    BuildingSerializer, UnitSerializer, ODFormSerializer, BuildingImageSerializer,
    UnitImageSerializer
)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class ODFormViewSet(viewsets.ModelViewSet):
    queryset = ODForm.objects.all()
    serializer_class = ODFormSerializer


class BuildingImageViewSet(viewsets.ModelViewSet):
    queryset = ODForm.objects.all()
    serializer_class = BuildingImageSerializer


class UnitImageViewSet(viewsets.ModelViewSet):
    queryset = ODForm.objects.all()
    serializer_class = UnitImageSerializer
