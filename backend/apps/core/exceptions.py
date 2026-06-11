from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

# Error Code Definitions
ERROR_CODES = {
    # Stock Errors (STOCK_***)
    'STOCK_001': 'Insufficient stock available',
    'STOCK_002': 'Stock cannot be negative',
    'STOCK_003': 'Invalid stock quantity',
    
    # Medicine Errors (MED_***)
    'MED_001': 'Medicine not found',
    'MED_002': 'Medicine already exists',
    'MED_003': 'Invalid medicine data',
    'MED_004': 'Medicine expired',
    'MED_005': 'Low stock alert',
    
    # Bill Errors (BILL_***)
    'BILL_001': 'Unable to generate bill',
    'BILL_002': 'Bill not found',
    'BILL_003': 'Invalid bill items',
    'BILL_004': 'Bill already finalized',
    
    # Location Errors (LOC_***)
    'LOC_001': 'Shelf not found',
    'LOC_002': 'Box not found',
    'LOC_003': 'Invalid location',
    
    # Validation Errors (VAL_***)
    'VAL_001': 'Invalid input data',
    'VAL_002': 'Missing required field',
    'VAL_003': 'Invalid date format',
    
    # Company Errors (COMP_***)
    'COMP_001': 'Company not found',
    'COMP_002': 'Company already exists',
    
    # User Errors (USER_***)
    'USER_001': 'User not found',
    'USER_002': 'Unauthorized access',
    'USER_003': 'Invalid credentials',
    
    # System Errors (SYS_***)
    'SYS_001': 'Database error',
    'SYS_002': 'Server error',
    'SYS_003': 'Operation failed',
}


class PharmacyException(Exception):
    """Base exception for pharmacy system"""
    def __init__(self, error_code, message=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.error_code = error_code
        self.message = message or ERROR_CODES.get(error_code, 'Unknown error')
        self.status_code = status_code
        super().__init__(self.message)


class StockException(PharmacyException):
    """Stock-related errors"""
    def __init__(self, error_code, message=None):
        super().__init__(error_code, message, status.HTTP_400_BAD_REQUEST)


class MedicineException(PharmacyException):
    """Medicine-related errors"""
    def __init__(self, error_code, message=None, status_code=status.HTTP_404_NOT_FOUND):
        super().__init__(error_code, message, status_code)


class BillingException(PharmacyException):
    """Billing-related errors"""
    def __init__(self, error_code, message=None):
        super().__init__(error_code, message, status.HTTP_400_BAD_REQUEST)


class LocationException(PharmacyException):
    """Location-related errors"""
    def __init__(self, error_code, message=None, status_code=status.HTTP_404_NOT_FOUND):
        super().__init__(error_code, message, status_code)


def custom_exception_handler(exc, context):
    """Custom exception handler for DRF"""
    
    # Handle custom pharmacy exceptions
    if isinstance(exc, PharmacyException):
        data = {
            'error_code': exc.error_code,
            'message': exc.message,
            'status': 'error',
        }
        return Response(data, status=exc.status_code)
    
    # Default handler for other exceptions
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data['status'] = 'error'
    else:
        # Unhandled exception - return generic error
        return Response(
            {
                'error_code': 'SYS_002',
                'message': ERROR_CODES['SYS_002'],
                'status': 'error',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
    return response