from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from pronovetai_app.views import (
    AddressViewSet, UserViewSet, CompanyViewSet, ContactViewSet,
    BuildingViewSet, UnitViewSet, ODFormViewSet
)

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'units', UnitViewSet)
router.register(r'odforms', ODFormViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]