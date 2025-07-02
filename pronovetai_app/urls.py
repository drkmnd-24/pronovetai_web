from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from pronovetai_app.views import (
    AddressViewSet, UserViewSet, CompanyViewSet, ContactViewSet,
    BuildingViewSet, UnitViewSet, ODFormViewSet, BuildingImageViewSet,
    UnitImageViewSet, StaffRegistrationView, ManagerRegistrationView,
    CurrentUserLogsView, ChangePasswordView, dashboard
)

from .auth_views import CustomTokenObtainPairView

from django.urls import path
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'units', UnitViewSet)
router.register(r'odforms', ODFormViewSet)
router.register(r'building-images', BuildingImageViewSet)
router.register(r'unit-images', UnitImageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/register/staff', StaffRegistrationView.as_view(), name='staff_registration'),
    path('api/register/manager', ManagerRegistrationView.as_view(), name='manager_registration'),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/users/me/', UserViewSet.as_view(), name='current_user'),
    path('api/users/me/logs', CurrentUserLogsView.as_view(), name='current_user_logs'),
    path('api/users/me/change_password/', ChangePasswordView.as_view(), name='change_password'),

    path('api/dashboard/', dashboard, name='dashboard'),
    # ======================= FRONT-END TEMPLATES ================================= #
    path('', TemplateView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('buildinglist/', TemplateView.as_view(template_name='building_list.html'), name='building_list'),
    path('unitlist/', TemplateView.as_view(template_name='unit_list.html'), name='unit_list'),
    path('companylist/', TemplateView.as_view(template_name='company_list.html'), name='company_list'),
    path('odformlist/', TemplateView.as_view(template_name='odform_list.html'), name='odform_list'),
]
