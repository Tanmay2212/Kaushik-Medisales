from rest_framework import serializers
from apps.inventory.models import Company, Shelf, Box, Medicine, AlternateMedicine
from django.core.exceptions import ValidationError


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for pharmaceutical companies"""
    class Meta:
        model = Company
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ShelfSerializer(serializers.ModelSerializer):
    """Serializer for shelves"""
    class Meta:
        model = Shelf
        fields = ['id', 'shelf_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class BoxSerializer(serializers.ModelSerializer):
    """Serializer for boxes with shelf detail"""
    shelf = ShelfSerializer(read_only=True)
    shelf_id = serializers.PrimaryKeyRelatedField(
        queryset=Shelf.objects.all(),
        write_only=True,
        source='shelf'
    )
    location_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Box
        fields = ['id', 'shelf', 'shelf_id', 'box_name', 'location_code', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'location_code']


class MedicineListSerializer(serializers.ModelSerializer):
    """Simplified medicine serializer for lists"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    location_code = serializers.CharField(source='location.location_code', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'medicine_name', 'company_name', 'salt_composition',
            'stock_quantity', 'minimum_stock', 'is_low_stock',
            'location_code', 'selling_price', 'expiry_date'
        ]


class MedicineDetailSerializer(serializers.ModelSerializer):
    """Detailed medicine serializer with all information"""
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        write_only=True,
        source='company'
    )
    location = BoxSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Box.objects.all(),
        write_only=True,
        source='location'
    )
    
    is_low_stock = serializers.BooleanField(read_only=True)
    profit_margin = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    profit_margin_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'medicine_name', 'company', 'company_id', 'salt_composition',
            'stock_quantity', 'minimum_stock', 'purchase_price', 'selling_price',
            'profit_margin', 'profit_margin_percentage', 'location', 'location_id',
            'expiry_date', 'barcode', 'is_low_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_low_stock', 'profit_margin', 'profit_margin_percentage']
    
    def validate(self, data):
        """Validate medicine data"""
        if data.get('selling_price', 0) < 0:
            raise serializers.ValidationError({"selling_price": "Selling price cannot be negative"})
        if data.get('purchase_price', 0) < 0:
            raise serializers.ValidationError({"purchase_price": "Purchase price cannot be negative"})
        if data.get('stock_quantity', 0) < 0:
            raise serializers.ValidationError({"stock_quantity": "Stock quantity cannot be negative"})
        return data


class AlternateMedicineSerializer(serializers.ModelSerializer):
    """Serializer for alternate medicines"""
    medicine = MedicineListSerializer(read_only=True)
    alternate_medicine = MedicineListSerializer(read_only=True)
    alternate_medicine_id = serializers.PrimaryKeyRelatedField(
        queryset=Medicine.objects.all(),
        write_only=True,
        source='alternate_medicine'
    )
    
    class Meta:
        model = AlternateMedicine
        fields = [
            'id', 'medicine', 'alternate_medicine', 'alternate_medicine_id',
            'salt_match_percentage', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_salt_match_percentage(self, value):
        """Validate salt match percentage is between 0-100"""
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Salt match percentage must be between 0 and 100")
        return value
