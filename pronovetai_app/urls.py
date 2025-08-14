from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from pronovetai_app.views import (
    AddressViewSet, UserViewSet, CompanyViewSet, ContactViewSet,
    BuildingViewSet, UnitViewSet, ODFormViewSet, BuildingImageViewSet,
    UnitImageViewSet, ExpiringContactView,

    StaffRegistrationView, ManagerRegistrationView,
    CurrentUserLogsView, ChangePasswordView,

    LoginView, LogoutView, dashboard_stats, dashboard_page,
    AdminUserViewSet
)

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'units', UnitViewSet)
router.register(r'odforms', ODFormViewSet)
router.register(r'building-images', BuildingImageViewSet)
router.register(r'unit-images', UnitImageViewSet)
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')


def secure_template(name: str):
    return login_required(TemplateView.as_view(template_name=name))


urlpatterns = [
    # ── DRF router ──────────────────────────────
    path("api/", include(router.urls)),

    # ── Auth (session + JWT) ────────────────────
    path("api/login/", LoginView.as_view(), name="api_login"),
    path("api/logout/", LogoutView.as_view(), name="api_logout"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ── User management extras ──────────────────
    path("api/register/staff/", StaffRegistrationView.as_view(), name="staff_registration"),
    path("api/register/manager/", ManagerRegistrationView.as_view(), name="manager_registration"),
    path("api/users/me/", UserViewSet.as_view(), name="current_user"),
    path("api/users/me/logs/", CurrentUserLogsView.as_view(), name="current_user_logs"),
    path("api/users/me/change_password/", ChangePasswordView.as_view(), name="change_password"),

    # ── Dashboard counters (JSON) ───────────────
    path("api/dashboard/", dashboard_stats, name="api_dashboard"),

    # ── Back-end Routes ──────────────────
    path("api/contacts/expiring", ExpiringContactView.as_view()),

    # ── Front-end templates (session required) ──
    path("", TemplateView.as_view(template_name='login.html'), name='login_page'),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("buildinglist/", secure_template("building_list.html"), name="building_list"),
    path("unitlist/", secure_template("unit_list.html"), name="unit_list"),
    path("companylist/", secure_template("company_list.html"), name="company_list"),
    path("odformlist/", secure_template("odform_list.html"), name="odform_list"),
    path("contactlist/", secure_template("contact_list.html"), name="contact_list"),
    path('userlist/', secure_template('user_list.html'), name='user_list'),
]
