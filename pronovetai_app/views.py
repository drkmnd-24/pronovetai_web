from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import AllowAny
from .models import (
    Address, User, Company, Contact, Building, Unit, ODForm,
    BuildingImage, UnitImage, UserLog
)
from .serializers import (
    AddressSerializer, UserSerializer, CompanySerializer, ContactSerializer,
    BuildingSerializer, UnitSerializer, ODFormSerializer, BuildingImageSerializer,
    UnitImageSerializer, StaffRegistrationSerializer, ManagerRegistrationSerializer,
    UserLogSerializer, ChangePasswordSerializer
)


class StaffRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class ManagerRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerRegistrationSerializer
    permission_classes = [permissions.IsAdminUser]


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


# This view is used to get the current logged-in user's data.
class UserViewSet(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CurrentUserLogsView(generics.ListAPIView):
    serializer_class = UserLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.logs.all().order_by('-timestamp')


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


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
    queryset = BuildingImage.objects.all()
    serializer_class = BuildingImageSerializer


class UnitImageViewSet(viewsets.ModelViewSet):
    queryset = UnitImage.objects.all()
    serializer_class = UnitImageSerializer
