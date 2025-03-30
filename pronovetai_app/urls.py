from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

from pronovetai_app.views import (
    AddressViewSet, UserViewSet, CompanyViewSet, ContactViewSet,
    BuildingViewSet, UnitViewSet, ODFormViewSet, BuildingImageViewSet,
    UnitImageViewSet, StaffRegistrationView, ManagerRegistrationView
)

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'units', UnitViewSet)
router.register(r'odforms', ODFormViewSet)
router.register(r'building-images', BuildingImageViewSet)
router.register(r'unit-images', UnitImageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/register/staff', StaffRegistrationView.as_view(), name='staff_registration'),
    path('api/register/manager', ManagerRegistrationView.as_view(), name='manager_registration'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]