from datetime import timedelta

from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from rest_framework import generics, viewsets, permissions, status

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Address, User, Company, Contact, Building, Unit, ODForm,
    BuildingImage, UnitImage, BuildingLog,
)
from .serializers import (
    AddressSerializer, UserSerializer, CompanySerializer, ContactSerializer,
    BuildingSerializer, UnitSerializer, ODFormSerializer, BuildingImageSerializer,
    UnitImageSerializer, StaffRegistrationSerializer, ManagerRegistrationSerializer,
    UserLogSerializer, ChangePasswordSerializer, BuildingLogSerializer,
)

API_AUTH = [JWTAuthentication, SessionAuthentication]


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_page(request):
    return render(request, 'dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    return Response({
        'buildings': Building.objects.count(),
        'units': Unit.objects.count(),
        'companies': Company.objects.count(),
        'contact': Contact.objects.count(),
        'odforms': ODForm.objects.count(),
        'users': User.objects.count(),
    })


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_destroy(self, instance: User):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'detail': 'Invalid Credentials'},
                            status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        access['is_staff'] = user.is_staff
        access['is_superuser'] = user.is_superuser

        access['username'] = user.username
        access['user_login'] = user.username
        access['first_name'] = user.first_name or ''
        access['last_name'] = user.last_name or ''

        return Response({
            'access': str(access),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffRegistrationSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        user = self.get_serializer().instance
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token  # a mutable token instance

        access["username"] = user.username
        access["user_login"] = user.username  # keep your legacy key
        access["first_name"] = user.first_name or ""
        access["last_name"] = user.last_name or ""

        return Response({
            "access": str(access),  # use the customised access token
            "refresh": str(refresh),
        })


class ManagerRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerRegistrationSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


# This view is used to get the current logged-in user's data.
class UserViewSet(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    queryset = Contact.objects.select_related('company')
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = API_AUTH


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class BuildingLogListCreateView(generics.ListCreateAPIView):
    serializer_class = BuildingLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        bldg_id = self.kwargs['building_id']
        return BuildingLog.objects.select_related('user').filter(building_id=bldg_id)

    def perform_create(self, serializer):
        bldg_id = self.kwargs['building_id']
        serializer.save(building_id=bldg_id, user=self.request.user)


class BuildingLogDestroyView(generics.DestroyAPIView):
    serializer_class = BuildingLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        bldg_id = self.kwargs['building_id']
        return BuildingLog.objects.filter(building_id=bldg_id)


class UnitPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('building')
    serializer_class = UnitSerializer
    pagination_class = UnitPagination


class ODFormViewSet(viewsets.ModelViewSet):
    queryset = ODForm.objects.all()
    serializer_class = ODFormSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            account_manager=user,
            created_by=user,
            edited_by=user,
        )

    def perform_update(self, serializer):
        serializer.save(edited_by=self.request.user)


class BuildingImageViewSet(viewsets.ModelViewSet):
    queryset = BuildingImage.objects.all()
    serializer_class = BuildingImageSerializer
    authentication_classes = API_AUTH


class UnitImageViewSet(viewsets.ModelViewSet):
    queryset = UnitImage.objects.all()
    serializer_class = UnitImageSerializer
    authentication_classes = API_AUTH


class ExpiringContactView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = API_AUTH

    def get(self, request):
        horizon = now().date() + timedelta(days=183)  # ≈ six months
        units = (
            Unit.objects
            .filter(lease_expiry_date__range=[now().date(), horizon])
            .select_related('building')
            .prefetch_related('contacts', 'contacts__company')
        )

        rows = []
        for unit in units:
            for contact in unit.contacts.all():
                rows.append({
                    "id": contact.id,
                    "company": contact.company.name if contact.company else "",
                    "location": unit.building.address_city,
                    "building": unit.building.name,
                    "unit_name": unit.name,
                    "lease_expiry": unit.lease_expiry_date.strftime("%m/%d/%Y"),
                    "gfa": f"{unit.gross_floor_area:,}" if unit.gross_floor_area else "",
                })

        rows.sort(key=lambda r: r["lease_expiry"])
        return Response(rows)
