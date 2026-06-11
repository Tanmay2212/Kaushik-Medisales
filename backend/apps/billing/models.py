from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.inventory.models import Medicine
from decimal import Decimal


class Bill(TimeStampedModel):
    """
    Bill/Invoice model.
    
    Represents a single customer transaction/sale.
    Tracks total amount and billing date.
    """
    id = models.AutoField(primary_key=True)
    bill_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique bill identifier (e.g., BILL-2024-001)"
    )
    
    # Bill Details
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Bill creation timestamp"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total bill amount"
    )
    
    # User Tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bills_created',
        help_text="User who created the bill"
    )
    
    # Status
    PENDING = 'pending'
    FINALIZED = 'finalized'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (FINALIZED, 'Finalized'),
        (CANCELLED, 'Cancelled'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Bill status"
    )
    
    class Meta:
        db_table = 'billing_bill'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['bill_number']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {self.total_amount}"
    
    @property
    def item_count(self):
        """Get total number of items in bill"""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0


class BillItem(TimeStampedModel):
    """
    Individual line item in a bill.
    
    Represents one medicine entry in a bill.
    """
    id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent bill"
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name='bill_items',
        help_text="Medicine sold"
    )
    
    # Quantity and Pricing
    quantity = models.IntegerField(
        help_text="Quantity sold"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Unit selling price at time of sale"
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="quantity × price"
    )
    
    class Meta:
        db_table = 'billing_bill_item'
        ordering = ['bill', 'id']
        indexes = [
            models.Index(fields=['bill']),
            models.Index(fields=['medicine']),
        ]
    
    def __str__(self):
        return f"{self.bill.bill_number} - {self.medicine.medicine_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate subtotal on save"""
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
