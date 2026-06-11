from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlternateMedicineViewSet

router = DefaultRouter()
router.register(r'', AlternateMedicineViewSet, basename='alternate-medicine')

urlpatterns = [path('', include(router.urls))]
