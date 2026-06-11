from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.inventory.models import Medicine, Company, Shelf, Box, AlternateMedicine
from apps.inventory.serializers import (
    MedicineListSerializer,
    MedicineDetailSerializer,
    CompanySerializer,
    ShelfSerializer,
    BoxSerializer,
    AlternateMedicineSerializer,
)
from apps.inventory.filters import MedicineFilter, CompanyFilter, AlternateMedicineFilter
from apps.core.exceptions import MedicineException, LocationException, StockException
from apps.audit_logs.services import AuditLogService


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pharmaceutical companies.
    
    Endpoints:
    - GET /api/v1/inventory/companies/ - List all companies
    - POST /api/v1/inventory/companies/ - Create new company
    - GET /api/v1/inventory/companies/{id}/ - Get company details
    - PUT /api/v1/inventory/companies/{id}/ - Update company
    - DELETE /api/v1/inventory/companies/{id}/ - Delete company
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Log company creation"""
        company = serializer.save()
        AuditLogService.log_action(
            user=self.request.user,
            action='medicine_created',
            description=f'Company created: {company.name}',
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Log company updates"""
        old_name = self.get_object().name
        company = serializer.save()
        if old_name != company.name:
            AuditLogService.log_action(
                user=self.request.user,
                action='medicine_updated',
                description=f'Company renamed: {old_name} → {company.name}',
                ip_address=self.get_client_ip()
            )
    
    @staticmethod
    def get_client_ip(request=None):
        """Extract client IP address from request"""
        if request is None:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_client_ip(self):
        """Extract client IP"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ShelfViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shelves (top-level storage).
    
    Endpoints:
    - GET /api/v1/inventory/shelves/ - List all shelves
    - POST /api/v1/inventory/shelves/ - Create new shelf
    - GET /api/v1/inventory/shelves/{id}/ - Get shelf details
    - PUT /api/v1/inventory/shelves/{id}/ - Update shelf
    - DELETE /api/v1/inventory/shelves/{id}/ - Delete shelf
    
    Example: Shelf A, Shelf B, Shelf C
    """
    queryset = Shelf.objects.prefetch_related('boxes')
    serializer_class = ShelfSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['shelf_name']
    
    def perform_create(self, serializer):
        """Log shelf creation"""
        shelf = serializer.save()
        AuditLogService.log_action(
            user=self.request.user,
            action='medicine_created',
            description=f'Shelf created: {shelf.shelf_name}',
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Extract client IP"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class BoxViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing boxes (storage within shelves).
    
    Endpoints:
    - GET /api/v1/inventory/boxes/ - List all boxes
    - POST /api/v1/inventory/boxes/ - Create new box
    - GET /api/v1/inventory/boxes/{id}/ - Get box details
    - PUT /api/v1/inventory/boxes/{id}/ - Update box
    - DELETE /api/v1/inventory/boxes/{id}/ - Delete box
    
    Example: Shelf A → Box A1, A2, A3
    """
    queryset = Box.objects.select_related('shelf')
    serializer_class = BoxSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['shelf']
    ordering_fields = ['shelf', 'box_name']
    ordering = ['shelf', 'box_name']
    
    def perform_create(self, serializer):
        """Log box creation"""
        box = serializer.save()
        AuditLogService.log_action(
            user=self.request.user,
            action='medicine_created',
            description=f'Box created: {box.location_code}',
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Extract client IP"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class MedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for medicine inventory management.
    
    Core endpoints:
    - GET /api/v1/inventory/medicines/ - List medicines with filters
    - POST /api/v1/inventory/medicines/ - Add new medicine
    - GET /api/v1/inventory/medicines/{id}/ - Get medicine details
    - PUT /api/v1/inventory/medicines/{id}/ - Update medicine
    - PATCH /api/v1/inventory/medicines/{id}/ - Partial update
    - DELETE /api/v1/inventory/medicines/{id}/ - Delete medicine
    
    Search endpoints:
    - GET /api/v1/inventory/medicines/search/by-salt/ - Search by salt
    - GET /api/v1/inventory/medicines/search/by-barcode/ - Search by barcode
    - GET /api/v1/inventory/medicines/search/low-stock/ - Get low stock medicines
    - GET /api/v1/inventory/medicines/search/expiry-alert/ - Get expiring medicines
    
    Custom actions:
    - POST /api/v1/inventory/medicines/{id}/add-stock/ - Add stock
    - POST /api/v1/inventory/medicines/{id}/reduce-stock/ - Reduce stock
    - GET /api/v1/inventory/medicines/{id}/location/ - Get exact location
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MedicineFilter
    search_fields = ['medicine_name', 'salt_composition']
    ordering_fields = ['medicine_name', 'stock_quantity', 'expiry_date', 'selling_price']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Get medicines with related data"""
        return Medicine.objects.select_related(
            'company', 'location__shelf'
        ).prefetch_related('alternatives')
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve, simple for list"""
        if self.action == 'retrieve':
            return MedicineDetailSerializer
        return MedicineListSerializer
    
    def perform_create(self, serializer):
        """Log medicine creation"""
        medicine = serializer.save()
        AuditLogService.log_action(
            user=self.request.user,
            action='medicine_created',
            medicine=medicine,
            description=f'Medicine added: {medicine.medicine_name}',
            new_value=serializer.validated_data,
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Log medicine updates"""
        medicine = self.get_object()
        old_data = {
            'stock': medicine.stock_quantity,
            'price': str(medicine.selling_price),
            'expiry': str(medicine.expiry_date),
        }
        
        updated_medicine = serializer.save()
        
        new_data = {
            'stock': updated_medicine.stock_quantity,
            'price': str(updated_medicine.selling_price),
            'expiry': str(updated_medicine.expiry_date),
        }
        
        AuditLogService.log_action(
            user=self.request.user,
            action='medicine_updated',
            medicine=medicine,
            description=f'Medicine updated: {medicine.medicine_name}',
            old_value=old_data,
            new_value=new_data,
            ip_address=self.get_client_ip()
        )
    
    def perform_destroy(self, instance):
        """Log medicine deletion"""
        AuditLogService.log_action(
            user=self.request.user,
            action='medicine_deleted',
            medicine=instance,
            description=f'Medicine deleted: {instance.medicine_name}',
            ip_address=self.get_client_ip()
        )
        instance.delete()
    
    @action(detail=False, methods=['get'], url_path='search/by-salt')
    def search_by_salt(self, request):
        """
        Search medicines by salt composition.
        
        Query: GET /api/v1/inventory/medicines/search/by-salt/?salt=Paracetamol
        """
        salt_query = request.query_params.get('salt', '')
        
        if not salt_query:
            return Response(
                {
                    'error_code': 'VAL_002',
                    'message': 'Salt parameter is required',
                    'status': 'error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        medicines = self.get_queryset().filter(
            salt_composition__icontains=salt_query
        )
        
        if not medicines.exists():
            raise MedicineException('MED_001', f'No medicines found with salt: {salt_query}')
        
        serializer = self.get_serializer(medicines, many=True)
        return Response({
            'count': medicines.count(),
            'results': serializer.data,
            'status': 'success'
        })
    
    @action(detail=False, methods=['get'], url_path='search/by-barcode')
    def search_by_barcode(self, request):
        """
        Search medicine by barcode.
        
        Query: GET /api/v1/inventory/medicines/search/by-barcode/?barcode=1234567890
        """
        barcode = request.query_params.get('barcode', '')
        
        if not barcode:
            return Response(
                {
                    'error_code': 'VAL_002',
                    'message': 'Barcode parameter is required',
                    'status': 'error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            medicine = self.get_queryset().get(barcode=barcode)
            serializer = self.get_serializer(medicine)
            return Response({
                'result': serializer.data,
                'status': 'success'
            })
        except Medicine.DoesNotExist:
            raise MedicineException('MED_001', f'Medicine with barcode {barcode} not found')
    
    @action(detail=False, methods=['get'], url_path='search/low-stock')
    def low_stock_medicines(self, request):
        """
        Get all medicines below minimum stock level.
        
        Query: GET /api/v1/inventory/medicines/search/low-stock/
        """
        medicines = self.get_queryset().filter(
            stock_quantity__lt=models.F('minimum_stock')
        ).order_by('stock_quantity')
        
        if not medicines.exists():
            return Response({
                'count': 0,
                'results': [],
                'message': 'No low stock medicines found',
                'status': 'success'
            })
        
        serializer = self.get_serializer(medicines, many=True)
        return Response({
            'count': medicines.count(),
            'results': serializer.data,
            'status': 'success'
        })
    
    @action(detail=False, methods=['get'], url_path='search/expiry-alert')
    def expiry_alert_medicines(self, request):
        """
        Get medicines expiring within specified days.
        
        Query: GET /api/v1/inventory/medicines/search/expiry-alert/?days=30
        
        Returns medicines expiring within the next N days.
        Default: 30 days if not specified
        """
        from datetime import timedelta
        from django.utils import timezone
        
        days = int(request.query_params.get('days', 30))
        
        if days < 1:
            return Response(
                {
                    'error_code': 'VAL_001',
                    'message': 'Days must be greater than 0',
                    'status': 'error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        future_date = timezone.now().date() + timedelta(days=days)
        today = timezone.now().date()
        
        medicines = self.get_queryset().filter(
            expiry_date__lte=future_date,
            expiry_date__gte=today
        ).order_by('expiry_date')
        
        if not medicines.exists():
            return Response({
                'count': 0,
                'results': [],
                'message': f'No medicines expiring within {days} days',
                'status': 'success'
            })
        
        serializer = self.get_serializer(medicines, many=True)
        return Response({
            'count': medicines.count(),
            'results': serializer.data,
            'status': 'success'
        })
    
    @action(detail=True, methods=['get'])
    def location(self, request, pk=None):
        """
        Get exact physical location of a medicine.
        
        Query: GET /api/v1/inventory/medicines/{id}/location/
        
        Response: Shows Shelf > Box location code
        Example: Shelf A > Box A2
        """
        medicine = self.get_object()
        return Response({
            'medicine_id': medicine.id,
            'medicine_name': medicine.medicine_name,
            'shelf': medicine.location.shelf.shelf_name,
            'box': medicine.location.box_name,
            'location_code': medicine.location.location_code,
            'stock_quantity': medicine.stock_quantity,
            'status': 'success'
        })
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """
        Add stock to a medicine.
        
        POST /api/v1/inventory/medicines/{id}/add-stock/
        Body: {"quantity": 50}
        """
        medicine = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise StockException('STOCK_003', 'Quantity must be greater than 0')
            
            medicine.stock_quantity += quantity
            medicine.save()
            
            AuditLogService.log_action(
                user=request.user,
                action='stock_added',
                medicine=medicine,
                description=f'Stock added: {quantity} units',
                old_value={'stock': medicine.stock_quantity - quantity},
                new_value={'stock': medicine.stock_quantity},
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'medicine_id': medicine.id,
                'medicine_name': medicine.medicine_name,
                'quantity_added': quantity,
                'new_stock': medicine.stock_quantity,
                'status': 'success'
            })
        except ValueError:
            return Response(
                {
                    'error_code': 'VAL_001',
                    'message': 'Invalid quantity format',
                    'status': 'error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, pk=None):
        """
        Reduce stock of a medicine.
        
        POST /api/v1/inventory/medicines/{id}/reduce-stock/
        Body: {"quantity": 10}
        """
        medicine = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = int(quantity)
            
            if quantity <= 0:
                raise StockException('STOCK_003', 'Quantity must be greater than 0')
            
            if medicine.stock_quantity < quantity:
                raise StockException(
                    'STOCK_001',
                    f'Insufficient stock. Available: {medicine.stock_quantity}, Requested: {quantity}'
                )
            
            medicine.stock_quantity -= quantity
            medicine.save()
            
            AuditLogService.log_action(
                user=request.user,
                action='stock_removed',
                medicine=medicine,
                description=f'Stock reduced: {quantity} units',
                old_value={'stock': medicine.stock_quantity + quantity},
                new_value={'stock': medicine.stock_quantity},
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'medicine_id': medicine.id,
                'medicine_name': medicine.medicine_name,
                'quantity_removed': quantity,
                'new_stock': medicine.stock_quantity,
                'status': 'success'
            })
        except ValueError:
            return Response(
                {
                    'error_code': 'VAL_001',
                    'message': 'Invalid quantity format',
                    'status': 'error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AlternateMedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing alternate/substitute medicines.
    
    Endpoints:
    - GET /api/v1/inventory/alternates/ - List all alternate medicines
    - POST /api/v1/inventory/alternates/ - Add new alternate
    - GET /api/v1/inventory/alternates/{id}/ - Get alternate details
    - PUT /api/v1/inventory/alternates/{id}/ - Update alternate
    - DELETE /api/v1/inventory/alternates/{id}/ - Delete alternate
    
    Custom actions:
    - GET /api/v1/inventory/alternates/medicine/{id}/ - Get alternatives for a medicine
    """
    queryset = AlternateMedicine.objects.select_related(
        'medicine', 'alternate_medicine'
    )
    serializer_class = AlternateMedicineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AlternateMedicineFilter
    
    def perform_create(self, serializer):
        """Log alternate medicine creation"""
        alternate = serializer.save()
        AuditLogService.log_action(
            user=self.request.user,
            action='alternate_added',
            medicine=alternate.medicine,
            description=f'Alternate added: {alternate.medicine.medicine_name} → {alternate.alternate_medicine.medicine_name}',
            ip_address=self.get_client_ip()
        )
    
    @action(detail=False, methods=['get'], url_path='medicine/(?P<medicine_id>[^/.]+)')
    def get_alternatives(self, request, medicine_id=None):
        """
        Get all alternatives for a specific medicine.
        
        Query: GET /api/v1/inventory/alternates/medicine/{medicine_id}/
        
        Example:
        GET /api/v1/inventory/alternates/medicine/5/
        
        Returns all medicines that can substitute the requested medicine.
        """
        try:
            medicine = Medicine.objects.get(id=medicine_id)
        except Medicine.DoesNotExist:
            raise MedicineException('MED_001', f'Medicine with id {medicine_id} not found')
        
        alternates = self.get_queryset().filter(medicine=medicine).order_by('-salt_match_percentage')
        
        if not alternates.exists():
            return Response({
                'medicine_id': medicine.id,
                'medicine_name': medicine.medicine_name,
                'alternatives': [],
                'count': 0,
                'status': 'success'
            })
        
        serializer = self.get_serializer(alternates, many=True)
        return Response({
            'medicine_id': medicine.id,
            'medicine_name': medicine.medicine_name,
            'alternatives': serializer.data,
            'count': alternates.count(),
            'status': 'success'
        })
    
    def get_client_ip(self):
        """Extract client IP"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


from django.db import models  # Import at end to avoid circular imports
