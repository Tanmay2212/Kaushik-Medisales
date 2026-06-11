from rest_framework import serializers
from apps.billing.models import Bill, BillItem
from apps.inventory.serializers import MedicineListSerializer
from decimal import Decimal


class BillItemSerializer(serializers.ModelSerializer):
    """Serializer for individual bill items"""
    medicine = MedicineListSerializer(read_only=True)
    medicine_id = serializers.PrimaryKeyRelatedField(
        queryset='apps.inventory.models.Medicine',
        write_only=True,
        source='medicine'
    )
    
    class Meta:
        model = BillItem
        fields = ['id', 'medicine', 'medicine_id', 'quantity', 'price', 'subtotal', 'created_at']
        read_only_fields = ['subtotal', 'created_at']
    
    def validate_quantity(self, value):
        """Quantity must be positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate_price(self, value):
        """Price must be non-negative"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value


class BillListSerializer(serializers.ModelSerializer):
    """Simplified bill serializer for lists"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Bill
        fields = ['id', 'bill_number', 'date', 'total_amount', 'created_by_name', 'status', 'item_count']


class BillDetailSerializer(serializers.ModelSerializer):
    """Detailed bill serializer with all items"""
    items = BillItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'date', 'total_amount', 'created_by',
            'created_by_name', 'status', 'items', 'item_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['date', 'created_at', 'updated_at', 'created_by', 'items']


class BillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bills"""
    items = BillItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Bill
        fields = ['bill_number', 'items']
    
    def validate_bill_number(self, value):
        """Ensure bill number is unique"""
        if Bill.objects.filter(bill_number=value).exists():
            raise serializers.ValidationError("Bill number already exists")
        return value
    
    def validate_items(self, value):
        """Ensure at least one item in bill"""
        if not value:
            raise serializers.ValidationError("Bill must contain at least one item")
        return value
