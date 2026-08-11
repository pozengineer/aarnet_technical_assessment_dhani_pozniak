"""
Views for network topology API.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Connection, Device, Interface, Site
from .serializers import (ConnectionSerializer, DeviceSerializer,
                          InterfaceSerializer, SiteSerializer)


class SiteViewSet(viewsets.ModelViewSet):
    """ViewSet for Site model."""

    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for Device model."""

    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class InterfaceViewSet(viewsets.ModelViewSet):
    """ViewSet for Interface model."""

    queryset = Interface.objects.all()
    serializer_class = InterfaceSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Connection model."""

    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer


class TraceConnectionsView(APIView):
    """
    Custom endpoint to trace connections through infrastructure elements.

    Query Parameters:
    - type: 'site', 'device', or 'interface'
    - id: The integer ID of the element
    """

    def get(self, request):
        """Trace connections for a given infrastructure element."""
        trace_type = request.query_params.get('type')
        element_id = request.query_params.get('id')

        # Validate parameters
        if not trace_type or not element_id:
            return Response(
                {'error': 'Both "type" and "id" query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if trace_type not in ['site', 'device', 'interface']:
            return Response(
                {'error': 'type must be one of: site, device, interface'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            element_id = int(element_id)
        except ValueError:
            return Response(
                {'error': 'id must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Trace based on type
        if trace_type == 'interface':
            return self._trace_interface(element_id)
        elif trace_type == 'device':
            return self._trace_device(element_id)
        elif trace_type == 'site':
            return self._trace_site(element_id)

    def _trace_interface(self, interface_id):
        """
        Trace all connections where the interface is start or end node.
        """
        interface = get_object_or_404(Interface, id=interface_id)

        connections = Connection.objects.filter(
            Q(start_interface_id=interface_id) |
            Q(end_interface_id=interface_id)
        ).order_by('id')

        traced_object = {
            'type': 'interface',
            'id': interface.id,
            'name': interface.name,
            'device': {
                'id': interface.device.id,
                'name': interface.device.name,
            },
            'site': {
                'id': interface.device.site.id,
                'name': interface.device.site.name,
            }
        }

        return self._format_response(traced_object, connections)

    def _trace_device(self, device_id):
        """
        Trace all connections tied to the device and its interfaces.
        """
        device = get_object_or_404(Device, id=device_id)

        # Get all interfaces for this device
        device_interface_ids = device.interfaces.values_list('id', flat=True)

        # Get connections where device interfaces are start or end
        connections = Connection.objects.filter(
            Q(start_interface_id__in=device_interface_ids) |
            Q(end_interface_id__in=device_interface_ids)
        ).order_by('id')

        traced_object = {
            'type': 'device',
            'id': device.id,
            'name': device.name,
            'site': {
                'id': device.site.id,
                'name': device.site.name,
            }
        }

        return self._format_response(traced_object, connections)

    def _trace_site(self, site_id):
        """
        Trace all connections tied to the site and its devices/interfaces.
        """
        site = get_object_or_404(Site, id=site_id)

        # Get all devices for this site
        site_device_ids = site.devices.values_list('id', flat=True)

        # Get all interfaces for devices in this site
        site_interface_ids = Interface.objects.filter(
            device_id__in=site_device_ids
        ).values_list('id', flat=True)

        # Get connections where site interfaces are start or end
        connections = Connection.objects.filter(
            Q(start_interface_id__in=site_interface_ids) |
            Q(end_interface_id__in=site_interface_ids)
        ).order_by('id')

        traced_object = {
            'type': 'site',
            'id': site.id,
            'name': site.name,
        }

        return self._format_response(traced_object, connections)

    def _format_response(self, traced_object, connections):
        """Format the trace response."""
        serializer = ConnectionSerializer(connections, many=True)

        return Response({
            'traced_object': traced_object,
            'connections_count': connections.count(),
            'connections': serializer.data
        })
