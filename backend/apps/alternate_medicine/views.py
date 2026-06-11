from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AlternateMedicine
from inventory.models import Medicine
from .serializers import AlternateMedicineListSerializer, AlternateMedicineDetailSerializer, CreateAlternateMedicineSerializer

class AlternateMedicineViewSet(viewsets.ModelViewSet):
    queryset = AlternateMedicine.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAlternateMedicineSerializer
        elif self.action == 'retrieve':
            return AlternateMedicineDetailSerializer
        return AlternateMedicineListSerializer
    
    @action(detail=False, methods=['get'], url_path='medicine/(?P<medicine_id>[^/.]+)/list')
    def get_alternates_for_medicine(self, request, medicine_id=None):
        try:
            medicine = Medicine.objects.get(id=medicine_id)
        except Medicine.DoesNotExist:
            return Response({'error': '[MED_001] Medicine not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        min_match = int(request.query_params.get('min_match', 70))
        alternates = AlternateMedicine.get_alternates_for_medicine(medicine_id, min_match)
        serializer = AlternateMedicineListSerializer(alternates, many=True)
        return Response({'medicine': medicine.medicine_name, 'alternates': serializer.data, 'count': len(serializer.data)})
    
    @action(detail=False, methods=['post'])
    def calculate_match(self, request):
        medicine_id = request.data.get('medicine_id')
        alternate_id = request.data.get('alternate_medicine_id')
        try:
            m1 = Medicine.objects.get(id=medicine_id)
            m2 = Medicine.objects.get(id=alternate_id)
        except Medicine.DoesNotExist:
            return Response({'error': '[MED_001] Medicine not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        match = AlternateMedicine.calculate_salt_match(m1.salt_composition, m2.salt_composition)
        return Response({'medicine1': m1.medicine_name, 'medicine2': m2.medicine_name, 'match_percentage': match})
