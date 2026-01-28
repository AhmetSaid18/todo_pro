from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
import redis

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Production health check endpoint for Docker, Kubernetes, Load Balancers
    """
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
    }
    
    # Database check
    try:
        connection.ensure_connection()
        status['database'] = 'connected'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['database'] = f'error: {str(e)}'
    
    # Redis/Cache check
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['cache'] = 'connected'
        else:
            status['cache'] = 'not responding'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['cache'] = f'error: {str(e)}'
    
    http_status = 200 if status['status'] == 'healthy' else 503
    return Response(status, status=http_status)
