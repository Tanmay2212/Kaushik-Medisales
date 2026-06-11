from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.inventory import views

app_name = 'inventory'

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'shelves', views.ShelfViewSet, basename='shelf')
router.register(r'boxes', views.BoxViewSet, basename='box')
router.register(r'medicines', views.MedicineViewSet, basename='medicine')
router.register(r'alternates', views.AlternateMedicineViewSet, basename='alternate')

urlpatterns = [
    path('', include(router.urls)),
]
