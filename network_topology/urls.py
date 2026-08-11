"""
URL configuration for network_topology project.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter

from topology import views

router = DefaultRouter()
router.register(r'sites', views.SiteViewSet, basename='site')
router.register(r'devices', views.DeviceViewSet, basename='device')
router.register(r'interfaces', views.InterfaceViewSet, basename='interface')
router.register(r'connections', views.ConnectionViewSet, basename='connection')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/trace/', views.TraceConnectionsView.as_view(), name='trace-connections'),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
