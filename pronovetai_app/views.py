from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Address, User, Company, Contact, Building, Unit, ODForm,
    BuildingImage, UnitImage
)
from .serializers import (
    AddressSerializer, UserSerializer, CompanySerializer, ContactSerializer,
    BuildingSerializer, UnitSerializer, ODFormSerializer, BuildingImageSerializer,
    UnitImageSerializer, StaffRegistrationSerializer, ManagerRegistrationSerializer,
    UserLogSerializer, ChangePasswordSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    return Response({
        'buildings': Building.objects.count(),
        'units': Unit.objects.count(),
        'companies': Company.objects.count(),
        'contact': Contact.objects.count(),
        'odforms': ODForm.objects.count(),
    })


class StaffRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffRegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        user = self.get_serializer().instance
        refresh = RefreshToken.for_user(user)
        resp.data['access'] = str(refresh.access_token)
        resp.data['refresh'] = str(refresh)
        return resp


class ManagerRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerRegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}


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
    queryset = Unit.objects.select_related('building')
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
