from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.inventory.models import Medicine


class AuditLog(TimeStampedModel):
    """
    Audit log model - Track all changes to inventory and billing.
    
    Maintains complete audit trail for compliance and debugging.
    """
    id = models.AutoField(primary_key=True)
    
    # User Info
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    
    # Action Details
    ACTION_CHOICES = [
        ('stock_added', 'Stock Added'),
        ('stock_removed', 'Stock Removed'),
        ('medicine_created', 'Medicine Created'),
        ('medicine_updated', 'Medicine Updated'),
        ('medicine_deleted', 'Medicine Deleted'),
        ('bill_created', 'Bill Created'),
        ('bill_finalized', 'Bill Finalized'),
        ('bill_cancelled', 'Bill Cancelled'),
        ('alternate_added', 'Alternate Medicine Added'),
        ('price_changed', 'Price Changed'),
        ('expiry_updated', 'Expiry Date Updated'),
    ]
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Action performed"
    )
    
    # Medicine Reference
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Medicine affected (if applicable)"
    )
    
    # Change Tracking
    old_value = models.TextField(
        blank=True,
        help_text="Previous value (JSON format)"
    )
    new_value = models.TextField(
        blank=True,
        help_text="New value (JSON format)"
    )
    
    # Context
    description = models.TextField(
        blank=True,
        help_text="Additional context about the change"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    
    class Meta:
        db_table = 'audit_logs_audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['medicine']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.user} - {self.created_at}"
