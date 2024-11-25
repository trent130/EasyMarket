from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Transaction

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request, transaction_id):
    """API endpoint to check payment status."""
    try:
        transaction = get_object_or_404(
            Transaction, 
            transaction_id=transaction_id,
            user=request.user
        )
        
        data = {
            'status': transaction.status,
            'message': transaction.get_status_display(),
            'redirect_url': None
        }
        
        if transaction.status == 'completed':
            data['redirect_url'] = f'/payment/confirmation/{transaction.id}/'
        elif transaction.status == 'failed':
            data['redirect_url'] = '/payment/failed/'
            
        return Response(data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )