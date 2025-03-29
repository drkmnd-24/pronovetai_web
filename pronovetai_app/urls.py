from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from pronovetai_app.views import BuildingViewSet, UnitViewSet, CompanyViewSet

router = routers.DefaultRouter()
router.register(r'buildings', BuildingViewSet)
router.register(r'units', UnitViewSet)
router.register(r'companies', CompanyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
