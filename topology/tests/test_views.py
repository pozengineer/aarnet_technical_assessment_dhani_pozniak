"""
Unit tests for topology views.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from topology.models import Connection, Device, Interface, Site


class SiteViewSetTests(APITestCase):
    """Test cases for SiteViewSet."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.site_data = {
            'name': 'London',
            'description': 'Primary data center',
            'status': 'Active'
        }
        self.site = Site.objects.create(**self.site_data)

    def test_list_sites(self):
        """Test listing all sites."""
        response = self.client.get('/api/sites/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_create_site(self):
        """Test creating a new site."""
        data = {
            'name': 'Paris',
            'description': 'Secondary data center',
            'status': 'Planned'
        }
        response = self.client.post('/api/sites/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Paris')
        self.assertTrue(Site.objects.filter(name='Paris').exists())

    def test_retrieve_site(self):
        """Test retrieving a single site."""
        response = self.client.get(f'/api/sites/{self.site.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'London')

    def test_retrieve_nonexistent_site(self):
        """Test retrieving a nonexistent site."""
        response = self.client.get('/api/sites/99999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_site(self):
        """Test updating a site."""
        data = {'status': 'Decommissioned'}
        response = self.client.patch(f'/api/sites/{self.site.id}/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.site.refresh_from_db()
        self.assertEqual(self.site.status, 'Decommissioned')

    def test_delete_site(self):
        """Test deleting a site."""
        site_id = self.site.id
        response = self.client.delete(f'/api/sites/{site_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Site.objects.filter(id=site_id).exists())

    def test_create_site_missing_name(self):
        """Test creating site without required name."""
        data = {'status': 'Active'}
        response = self.client.post('/api/sites/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_site_duplicate_name(self):
        """Test creating site with duplicate name."""
        data = self.site_data.copy()
        response = self.client.post('/api/sites/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeviceViewSetTests(TestCase):
    """Test cases for DeviceViewSet."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name='DataCenter1', status='Active')
        self.device = Device.objects.create(
            name='Router-01',
            site=self.site,
            serial_number='SN123456'
        )

    def test_device_serializer_includes_site_name(self):
        """Test that device serializer includes site_name."""
        from topology.serializers import DeviceSerializer
        serializer = DeviceSerializer(self.device)

        self.assertEqual(serializer.data['site_name'], 'DataCenter1')
        self.assertEqual(serializer.data['name'], 'Router-01')

    def test_device_creation(self):
        """Test device creation and retrieval."""
        device = Device.objects.create(
            name='Router-02',
            site=self.site,
            serial_number='SN654321'
        )

        self.assertEqual(device.name, 'Router-02')
        self.assertEqual(device.serial_number, 'SN654321')
        self.assertEqual(device.site, self.site)

    def test_device_site_relationship(self):
        """Test device site foreign key relationship."""
        self.assertEqual(self.device.site.name, 'DataCenter1')

    def test_device_queryset(self):
        """Test querying devices."""
        devices = Device.objects.filter(name='Router-01')
        self.assertTrue(devices.exists())
        self.assertEqual(devices.first().serial_number, 'SN123456')


class InterfaceViewSetTests(TestCase):
    """Test cases for InterfaceViewSet."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name='DataCenter1', status='Active')
        self.device = Device.objects.create(
            name='Router-01',
            site=self.site,
            serial_number='SN123456'
        )
        self.interface = Interface.objects.create(
            name='eth0',
            device=self.device,
            speed=1000,
            status='Up'
        )

    def test_interface_serializer_includes_device_name(self):
        """Test that interface serializer includes device_name."""
        from topology.serializers import InterfaceSerializer
        serializer = InterfaceSerializer(self.interface)

        self.assertEqual(serializer.data['device_name'], 'Router-01')
        self.assertEqual(serializer.data['name'], 'eth0')
        self.assertEqual(serializer.data['speed'], 1000)

    def test_interface_creation(self):
        """Test interface creation and retrieval."""
        interface = Interface.objects.create(
            name='eth1',
            device=self.device,
            speed=100,
            status='Down'
        )

        self.assertEqual(interface.name, 'eth1')
        self.assertEqual(interface.speed, 100)
        self.assertEqual(interface.device, self.device)

    def test_interface_device_relationship(self):
        """Test interface device foreign key relationship."""
        self.assertEqual(self.interface.device.name, 'Router-01')
        self.assertEqual(str(self.interface), 'Router-01/eth0')

    def test_interface_queryset(self):
        """Test querying interfaces."""
        interfaces = Interface.objects.filter(device=self.device)
        self.assertTrue(interfaces.exists())
        self.assertEqual(interfaces.first().name, 'eth0')


class ConnectionViewSetTests(TestCase):
    """Test cases for ConnectionViewSet."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name='DataCenter1', status='Active')
        self.device1 = Device.objects.create(
            name='Router-01',
            site=self.site,
            serial_number='SN111111'
        )
        self.device2 = Device.objects.create(
            name='Router-02',
            site=self.site,
            serial_number='SN222222'
        )
        self.interface1 = Interface.objects.create(
            name='eth0',
            device=self.device1,
            speed=1000
        )
        self.interface2 = Interface.objects.create(
            name='eth0',
            device=self.device2,
            speed=1000
        )
        self.connection = Connection.objects.create(
            connection_id='CONN001',
            name='Link1',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )

    def test_connection_serializer_includes_targets(self):
        """Test that connection serializer includes start_target and end_target."""
        from topology.serializers import ConnectionSerializer
        serializer = ConnectionSerializer(self.connection)

        self.assertIn('start_target', serializer.data)
        self.assertIn('end_target', serializer.data)
        self.assertIn('site', serializer.data['start_target'])
        self.assertIn('device', serializer.data['start_target'])
        self.assertIn('interface', serializer.data['start_target'])

    def test_connection_creation(self):
        """Test connection creation and retrieval."""
        connection = Connection.objects.create(
            connection_id='CONN002',
            name='Link2',
            status='Disconnected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )

        self.assertEqual(connection.connection_id, 'CONN002')
        self.assertEqual(connection.status, 'Disconnected')

    def test_connection_interface_relationship(self):
        """Test connection interface foreign key relationships."""
        self.assertEqual(self.connection.start_interface, self.interface1)
        self.assertEqual(self.connection.end_interface, self.interface2)

    def test_connection_queryset(self):
        """Test querying connections."""
        connections = Connection.objects.filter(connection_id='CONN001')
        self.assertTrue(connections.exists())
        self.assertEqual(connections.first().name, 'Link1')


class TraceConnectionsViewTests(APITestCase):
    """Test cases for TraceConnectionsView."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.site = Site.objects.create(name='DataCenter1', status='Active')
        self.device1 = Device.objects.create(
            name='Router-01',
            site=self.site,
            serial_number='SN111111'
        )
        self.device2 = Device.objects.create(
            name='Router-02',
            site=self.site,
            serial_number='SN222222'
        )
        self.interface1 = Interface.objects.create(
            name='eth0',
            device=self.device1,
            speed=1000
        )
        self.interface2 = Interface.objects.create(
            name='eth0',
            device=self.device2,
            speed=1000
        )
        self.connection = Connection.objects.create(
            connection_id='CONN001',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )

    def test_trace_interface(self):
        """Test tracing connections for an interface."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'interface', 'id': self.interface1.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['traced_object']['type'], 'interface')
        self.assertGreater(response.data['connections_count'], 0)

    def test_trace_device(self):
        """Test tracing connections for a device."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'device', 'id': self.device1.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['traced_object']['type'], 'device')
        self.assertGreater(response.data['connections_count'], 0)

    def test_trace_site(self):
        """Test tracing connections for a site."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'site', 'id': self.site.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['traced_object']['type'], 'site')
        self.assertGreater(response.data['connections_count'], 0)

    def test_trace_missing_type_parameter(self):
        """Test trace endpoint with missing type parameter."""
        response = self.client.get('/api/trace/', {'id': self.interface1.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_trace_missing_id_parameter(self):
        """Test trace endpoint with missing id parameter."""
        response = self.client.get('/api/trace/', {'type': 'interface'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_trace_invalid_type(self):
        """Test trace endpoint with invalid type."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'invalid', 'id': self.interface1.id}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_trace_non_integer_id(self):
        """Test trace endpoint with non-integer id."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'interface', 'id': 'abc'}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_trace_nonexistent_interface(self):
        """Test trace endpoint with nonexistent interface id."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'interface', 'id': 99999}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_trace_nonexistent_device(self):
        """Test trace endpoint with nonexistent device id."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'device', 'id': 99999}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_trace_nonexistent_site(self):
        """Test trace endpoint with nonexistent site id."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'site', 'id': 99999}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_trace_interface_response_structure(self):
        """Test trace interface response has correct structure."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'interface', 'id': self.interface1.id}
        )

        self.assertIn('traced_object', response.data)
        self.assertIn('connections_count', response.data)
        self.assertIn('connections', response.data)

        traced = response.data['traced_object']
        self.assertIn('type', traced)
        self.assertIn('id', traced)
        self.assertIn('name', traced)

    def test_trace_device_response_structure(self):
        """Test trace device response has correct structure."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'device', 'id': self.device1.id}
        )

        traced = response.data['traced_object']
        self.assertEqual(traced['type'], 'device')
        self.assertIn('site', traced)

    def test_trace_site_response_structure(self):
        """Test trace site response has correct structure."""
        response = self.client.get(
            '/api/trace/',
            {'type': 'site', 'id': self.site.id}
        )

        traced = response.data['traced_object']
        self.assertEqual(traced['type'], 'site')
        self.assertNotIn('site', traced)
