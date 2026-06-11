from rest_framework import serializers
from apps.audit_logs.models import AuditLog
import json


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    old_value_parsed = serializers.SerializerMethodField()
    new_value_parsed = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'medicine', 'medicine_name',
            'old_value', 'old_value_parsed', 'new_value', 'new_value_parsed',
            'description', 'ip_address', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'medicine', 'medicine_name',
            'old_value', 'old_value_parsed', 'new_value', 'new_value_parsed',
            'created_at'
        ]
    
    def get_old_value_parsed(self, obj):
        """Parse JSON old_value"""
        if obj.old_value:
            try:
                return json.loads(obj.old_value)
            except json.JSONDecodeError:
                return obj.old_value
        return None
    
    def get_new_value_parsed(self, obj):
        """Parse JSON new_value"""
        if obj.new_value:
            try:
                return json.loads(obj.new_value)
            except json.JSONDecodeError:
                return obj.new_value
        return None


class AuditLogListSerializer(serializers.ModelSerializer):
    """Simplified audit log serializer for lists"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'action', 'medicine_name', 'description', 'created_at']
