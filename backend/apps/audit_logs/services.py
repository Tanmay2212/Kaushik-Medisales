import json
from apps.audit_logs.models import AuditLog
from django.contrib.auth.models import User


class AuditLogService:
    """
    Service for logging audit trail events.
    
    Handles creation of audit log entries with before/after values.
    """
    
    @staticmethod
    def log_action(
        user=None,
        action='',
        medicine=None,
        description='',
        old_value=None,
        new_value=None,
        ip_address=None
    ):
        """
        Create an audit log entry.
        
        Args:
            user: Django User object who performed the action
            action: Action type (e.g., 'stock_added', 'medicine_updated')
            medicine: Related Medicine object (optional)
            description: Human-readable description
            old_value: Previous value (dict or string)
            new_value: New value (dict or string)
            ip_address: User's IP address
        
        Returns:
            AuditLog instance
        """
        try:
            # Convert dict values to JSON
            old_value_json = json.dumps(old_value) if old_value else ''
            new_value_json = json.dumps(new_value) if new_value else ''
            
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                medicine=medicine,
                description=description,
                old_value=old_value_json,
                new_value=new_value_json,
                ip_address=ip_address
            )
            
            return audit_log
        except Exception as e:
            # Log service should not break main application
            print(f"Error creating audit log: {str(e)}")
            return None
    
    @staticmethod
    def get_medicine_history(medicine_id):
        """
        Get all audit log entries for a specific medicine.
        
        Args:
            medicine_id: Medicine ID
        
        Returns:
            QuerySet of AuditLog entries ordered by timestamp
        """
        return AuditLog.objects.filter(
            medicine_id=medicine_id
        ).order_by('-created_at')
    
    @staticmethod
    def get_user_actions(user_id):
        """
        Get all actions performed by a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            QuerySet of AuditLog entries ordered by timestamp
        """
        return AuditLog.objects.filter(
            user_id=user_id
        ).order_by('-created_at')
    
    @staticmethod
    def get_action_logs(action_type):
        """
        Get all logs for a specific action type.
        
        Args:
            action_type: Action type (e.g., 'stock_added')
        
        Returns:
            QuerySet of AuditLog entries ordered by timestamp
        """
        return AuditLog.objects.filter(
            action=action_type
        ).order_by('-created_at')
