from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.audit_logs import views

app_name = 'audit'

router = DefaultRouter()
router.register(r'logs', views.AuditLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
