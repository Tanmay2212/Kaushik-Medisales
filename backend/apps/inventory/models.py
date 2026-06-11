from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel


class Company(TimeStampedModel):
    """
    Pharmaceutical company model.
    
    Stores medicine manufacturers/companies.
    Example: Cipla, Dr. Reddy's, Lupin
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Company name (e.g., Cipla, Dr. Reddy's)"
    )
    
    class Meta:
        db_table = 'inventory_company'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Shelf(TimeStampedModel):
    """
    Shelf model for medicine storage organization.
    
    Top-level storage location.
    Example: A, B, C
    """
    id = models.AutoField(primary_key=True)
    shelf_name = models.CharField(
        max_length=10,
        unique=True,
        help_text="Shelf identifier (e.g., A, B, C)"
    )
    
    class Meta:
        db_table = 'inventory_shelf'
        ordering = ['shelf_name']
        indexes = [
            models.Index(fields=['shelf_name']),
        ]
    
    def __str__(self):
        return f"Shelf {self.shelf_name}"


class Box(TimeStampedModel):
    """
    Box model for detailed medicine storage organization.
    
    Second-level storage location within a shelf.
    Example: Shelf A > Box A1, A2, A3
    """
    id = models.AutoField(primary_key=True)
    shelf = models.ForeignKey(
        Shelf,
        on_delete=models.PROTECT,
        related_name='boxes',
        help_text="Parent shelf"
    )
    box_name = models.CharField(
        max_length=10,
        help_text="Box identifier within shelf (e.g., A1, A2)"
    )
    
    class Meta:
        db_table = 'inventory_box'
        unique_together = ['shelf', 'box_name']
        ordering = ['shelf', 'box_name']
        indexes = [
            models.Index(fields=['shelf', 'box_name']),
        ]
    
    def __str__(self):
        return f"{self.shelf.shelf_name} > {self.box_name}"
    
    @property
    def location_code(self):
        """Generate readable location code"""
        return f"{self.shelf.shelf_name}{self.box_name}"


class Medicine(TimeStampedModel):
    """
    Medicine/Drug model - Core inventory item.
    
    Stores complete medicine information with location tracking.
    """
    id = models.AutoField(primary_key=True)
    
    # Basic Info
    medicine_name = models.CharField(
        max_length=255,
        help_text="Medicine name (e.g., Dolo 650)"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='medicines',
        help_text="Manufacturer company"
    )
    salt_composition = models.CharField(
        max_length=500,
        help_text="Active salt/ingredient (e.g., Paracetamol 650mg)"
    )
    
    # Location
    location = models.ForeignKey(
        Box,
        on_delete=models.PROTECT,
        related_name='medicines',
        help_text="Storage location (Shelf > Box)"
    )
    
    # Stock Management
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity"
    )
    minimum_stock = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Minimum threshold for low stock alert"
    )
    
    # Pricing
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Cost price per unit"
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Selling price per unit"
    )
    
    # Tracking
    expiry_date = models.DateField(
        help_text="Medicine expiry date"
    )
    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Barcode for quick search (optional)"
    )
    
    class Meta:
        db_table = 'inventory_medicine'
        unique_together = ['medicine_name', 'company', 'expiry_date']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['medicine_name']),
            models.Index(fields=['salt_composition']),
            models.Index(fields=['company']),
            models.Index(fields=['barcode']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['stock_quantity']),
        ]
    
    def __str__(self):
        return f"{self.medicine_name} - {self.company.name}"
    
    @property
    def is_low_stock(self):
        """Check if medicine is below minimum stock level"""
        return self.stock_quantity < self.minimum_stock
    
    @property
    def profit_margin(self):
        """Calculate profit per unit"""
        if self.purchase_price == 0:
            return 0
        return self.selling_price - self.purchase_price
    
    @property
    def profit_margin_percentage(self):
        """Calculate profit margin percentage"""
        if self.purchase_price == 0:
            return 0
        return (self.profit_margin / self.purchase_price) * 100


class AlternateMedicine(TimeStampedModel):
    """
    Alternate/Substitute medicine model.
    
    Links similar medicines with same salt composition.
    Example: Dolo 650 -> Paracip 650, Crocin Advance
    """
    id = models.AutoField(primary_key=True)
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='alternatives',
        help_text="Original medicine"
    )
    alternate_medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='suggested_as_alternative',
        help_text="Suggested alternative medicine"
    )
    
    # Salt matching
    salt_match_percentage = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Salt composition match percentage"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this alternative"
    )
    
    class Meta:
        db_table = 'inventory_alternate_medicine'
        unique_together = ['medicine', 'alternate_medicine']
        ordering = ['-salt_match_percentage']
        indexes = [
            models.Index(fields=['medicine']),
            models.Index(fields=['alternate_medicine']),
        ]
    
    def __str__(self):
        return f"{self.medicine.medicine_name} -> {self.alternate_medicine.medicine_name} ({self.salt_match_percentage}%)"
    
    def clean(self):
        """Validate that medicine and alternate_medicine are different"""
        from django.core.exceptions import ValidationError
        if self.medicine_id == self.alternate_medicine_id:
            raise ValidationError("Medicine cannot be its own alternative")
