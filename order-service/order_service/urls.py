"""
URL configuration for order_service project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import datetime


def health_check(request):
    """
    Health check endpoint for container orchestration.
    Verifies that the service is ready to accept requests.
    
    Educational Note: Health checks are essential in microservices:
    - Docker uses them to know when a service is ready
    - Load balancers use them for routing decisions
    - Monitoring systems use them for alerting
    """
    from django.db import connection
    from django.conf import settings
    
    health_status = {
        'service': 'order-service',
        'checks': {},
        'timestamp': datetime.datetime.now().isoformat(),
    }
    
    # Check if JWT public key is loaded
    if hasattr(settings, 'JWT_PUBLIC_KEY') and settings.JWT_PUBLIC_KEY:
        health_status['checks']['jwt_public_key'] = 'ok'
    else:
        health_status['checks']['jwt_public_key'] = 'missing'
    
    # Check database connectivity
    try:
        connection.ensure_connection()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
    
    # Determine overall status
    if health_status['checks'].get('database') == 'ok':
        if health_status['checks'].get('jwt_public_key') == 'ok':
            health_status['status'] = 'healthy'
            status_code = 200
        else:
            health_status['status'] = 'degraded'  # Can start but auth won't work
            status_code = 200
    else:
        health_status['status'] = 'unhealthy'
        status_code = 503
    
    return JsonResponse(health_status, status=status_code)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/', include('orders.urls')),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
