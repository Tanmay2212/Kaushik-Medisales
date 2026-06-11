from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.audit_logs.models import AuditLog
from apps.audit_logs.serializers import AuditLogSerializer, AuditLogListSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs (read-only).
    
    Endpoints:
    - GET /api/v1/audit/logs/ - List all audit logs
    - GET /api/v1/audit/logs/{id}/ - Get specific log
    - GET /api/v1/audit/logs/medicine/{medicine_id}/ - Get logs for a medicine
    - GET /api/v1/audit/logs/user/{user_id}/ - Get logs for a user
    - GET /api/v1/audit/logs/action/{action_type}/ - Get logs for an action
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'medicine']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get audit logs with related data"""
        return AuditLog.objects.select_related(
            'user', 'medicine'
        ).prefetch_related('medicine__company').order_by('-created_at')
    
    def get_serializer_class(self):
        """Use list serializer for list view"""
        if self.action == 'list':
            return AuditLogListSerializer
        return AuditLogSerializer
    
    @action(detail=False, methods=['get'], url_path='medicine/(?P<medicine_id>[^/.]+)')
    def by_medicine(self, request, medicine_id=None):
        """
        Get all audit logs for a specific medicine.
        
        Query: GET /api/v1/audit/logs/medicine/{medicine_id}/
        """
        logs = self.get_queryset().filter(medicine_id=medicine_id)
        
        if not logs.exists():
            return Response({
                'medicine_id': medicine_id,
                'logs': [],
                'count': 0,
                'status': 'success'
            })
        
        serializer = AuditLogListSerializer(logs, many=True)
        return Response({
            'medicine_id': medicine_id,
            'logs': serializer.data,
            'count': logs.count(),
            'status': 'success'
        })
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """
        Get all actions performed by a specific user.
        
        Query: GET /api/v1/audit/logs/user/{user_id}/
        """
        logs = self.get_queryset().filter(user_id=user_id)
        
        if not logs.exists():
            return Response({
                'user_id': user_id,
                'logs': [],
                'count': 0,
                'status': 'success'
            })
        
        serializer = AuditLogListSerializer(logs, many=True)
        return Response({
            'user_id': user_id,
            'logs': serializer.data,
            'count': logs.count(),
            'status': 'success'
        })
    
    @action(detail=False, methods=['get'])
    def actions(self, request):
        """
        Get all unique action types with counts.
        
        Query: GET /api/v1/audit/logs/actions/
        """
        action_choices = dict(AuditLog.ACTION_CHOICES)
        action_counts = {}
        
        for action_key in action_choices.keys():
            count = AuditLog.objects.filter(action=action_key).count()
            if count > 0:
                action_counts[action_key] = {
                    'name': action_choices[action_key],
                    'count': count
                }
        
        return Response({
            'actions': action_counts,
            'total_actions': sum([v['count'] for v in action_counts.values()]),
            'status': 'success'
        })
