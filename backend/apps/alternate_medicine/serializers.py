from rest_framework import serializers
from .models import AlternateMedicine

class AlternateMedicineListSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    alternate_name = serializers.CharField(source='alternate_medicine.medicine_name', read_only=True)
    class Meta:
        model = AlternateMedicine
        fields = ['id', 'medicine_name', 'alternate_name', 'salt_match_percentage', 'is_active']

class AlternateMedicineDetailSerializer(serializers.ModelSerializer):
    medicine_details = serializers.SerializerMethodField()
    alternate_details = serializers.SerializerMethodField()
    class Meta:
        model = AlternateMedicine
        fields = ['id', 'medicine', 'medicine_details', 'alternate_medicine', 'alternate_details', 'salt_match_percentage', 'notes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_medicine_details(self, obj):
        m = obj.medicine
        return {'id': m.id, 'name': m.medicine_name, 'salt': m.salt_composition, 'stock': m.stock_quantity}
    
    def get_alternate_details(self, obj):
        m = obj.alternate_medicine
        return {'id': m.id, 'name': m.medicine_name, 'salt': m.salt_composition, 'stock': m.stock_quantity}

class CreateAlternateMedicineSerializer(serializers.ModelSerializer):
    auto_calculate_match = serializers.BooleanField(write_only=True, default=False)
    class Meta:
        model = AlternateMedicine
        fields = ['medicine', 'alternate_medicine', 'salt_match_percentage', 'notes', 'auto_calculate_match', 'is_active']
    
    def validate(self, data):
        medicine = data.get('medicine')
        alternate_medicine = data.get('alternate_medicine')
        if medicine and alternate_medicine and medicine.id == alternate_medicine.id:
            raise serializers.ValidationError('Cannot set same medicine as alternate.')
        return data
    
    def create(self, validated_data):
        auto_calculate = validated_data.pop('auto_calculate_match', False)
        if auto_calculate:
            medicine = validated_data.get('medicine')
            alternate = validated_data.get('alternate_medicine')
            match_percentage = AlternateMedicine.calculate_salt_match(medicine.salt_composition, alternate.salt_composition)
            validated_data['salt_match_percentage'] = match_percentage
        return AlternateMedicine.objects.create(**validated_data)
