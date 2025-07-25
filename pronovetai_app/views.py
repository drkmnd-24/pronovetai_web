from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render

from rest_framework import generics, viewsets, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
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


@login_required
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
        return Response({
            'access': str(refresh.access_token),
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
        resp.data['access'] = str(refresh.access_token)
        resp.data['refresh'] = str(refresh)
        return resp


class ManagerRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerRegistrationSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}


DEFAULT_AUTH = [SessionAuthentication, JWTAuthentication]


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
    queryset = Contact.objects.select_related('company')
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


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
    authentication_classes = DEFAULT_AUTH


class UnitImageViewSet(viewsets.ModelViewSet):
    queryset = UnitImage.objects.all()
    serializer_class = UnitImageSerializer
    authentication_classes = DEFAULT_AUTH
