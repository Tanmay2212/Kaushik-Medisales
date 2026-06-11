from django_filters import rest_framework as filters
from apps.inventory.models import Medicine, Company, AlternateMedicine


class MedicineFilter(filters.FilterSet):
    """
    Filter medicines by various criteria.
    
    Supports:
    - medicine_name (partial match)
    - salt_composition (partial match)
    - company (exact match)
    - barcode (exact match)
    - is_low_stock (boolean)
    - location (by box)
    """
    
    medicine_name = filters.CharFilter(
        field_name='medicine_name',
        lookup_expr='icontains',
        help_text='Search by medicine name (case-insensitive)'
    )
    
    salt_composition = filters.CharFilter(
        field_name='salt_composition',
        lookup_expr='icontains',
        help_text='Search by salt composition (case-insensitive)'
    )
    
    company = filters.ModelChoiceFilter(
        queryset=Company.objects.all(),
        help_text='Filter by company'
    )
    
    barcode = filters.CharFilter(
        field_name='barcode',
        lookup_expr='exact',
        help_text='Search by exact barcode'
    )
    
    is_low_stock = filters.BooleanFilter(
        method='filter_low_stock',
        help_text='Filter low stock medicines'
    )
    
    expiry_days = filters.NumberFilter(
        method='filter_expiry_days',
        help_text='Medicines expiring in N days (e.g., 30 for 30 days)'
    )
    
    class Meta:
        model = Medicine
        fields = ['medicine_name', 'salt_composition', 'company', 'barcode', 'is_low_stock']
    
    def filter_low_stock(self, queryset, name, value):
        """
        Filter medicines with stock below minimum threshold.
        """
        if value:
            # Get medicines where stock < minimum_stock
            return queryset.filter(stock_quantity__lt=models.F('minimum_stock'))
        return queryset
    
    def filter_expiry_days(self, queryset, name, value):
        """
        Filter medicines expiring within N days.
        """
        from datetime import timedelta
        from django.utils import timezone
        
        if value:
            future_date = timezone.now().date() + timedelta(days=int(value))
            return queryset.filter(
                expiry_date__lte=future_date,
                expiry_date__gte=timezone.now().date()
            )
        return queryset


from django.db import models  # Import at module level


class CompanyFilter(filters.FilterSet):
    """
    Filter companies by name.
    """
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Search by company name (case-insensitive)'
    )
    
    class Meta:
        model = Company
        fields = ['name']


class AlternateMedicineFilter(filters.FilterSet):
    """
    Filter alternate medicines.
    """
    medicine_name = filters.CharFilter(
        field_name='medicine__medicine_name',
        lookup_expr='icontains',
        help_text='Search by original medicine name'
    )
    
    salt_match_min = filters.NumberFilter(
        field_name='salt_match_percentage',
        lookup_expr='gte',
        help_text='Minimum salt match percentage'
    )
    
    class Meta:
        model = AlternateMedicine
        fields = ['medicine', 'salt_match_min']
