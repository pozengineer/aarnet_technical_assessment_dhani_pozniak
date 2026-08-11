"""
Unit tests for topology serializers.
"""

from django.test import TestCase
from rest_framework.test import APITestCase

from topology.models import Connection, Device, Interface, Site
from topology.serializers import (ConnectionSerializer, DeviceSerializer,
                                  InterfaceSerializer, SiteSerializer)


class SiteSerializerTests(TestCase):
    """Test cases for SiteSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(
            name='London',
            description='Primary data center',
            status='Active'
        )

    def test_serialize_site(self):
        """Test Site serialization."""
        serializer = SiteSerializer(self.site)
        data = serializer.data

        self.assertEqual(data['name'], 'London')
        self.assertEqual(data['description'], 'Primary data center')
        self.assertEqual(data['status'], 'Active')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_deserialize_site(self):
        """Test Site deserialization."""
        data = {
            'name': 'Paris',
            'description': 'European site',
            'status': 'Planned'
        }
        serializer = SiteSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        site = serializer.save()
        self.assertEqual(site.name, 'Paris')
        self.assertEqual(site.status, 'Planned')

    def test_update_site(self):
        """Test Site update."""
        data = {
            'name': 'London Updated',
            'description': 'Updated description',
            'status': 'Planned'
        }
        serializer = SiteSerializer(self.site, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        updated_site = serializer.save()
        self.assertEqual(updated_site.status, 'Planned')

    def test_site_required_fields(self):
        """Test required fields validation."""
        data = {'description': 'Missing name'}
        serializer = SiteSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class DeviceSerializerTests(TestCase):
    """Test cases for DeviceSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name='DataCenter1', status='Active')
        self.device = Device.objects.create(
            name='Router-01',
            site=self.site,
            serial_number='SN123456'
        )

    def test_serialize_device(self):
        """Test Device serialization."""
        serializer = DeviceSerializer(self.device)
        data = serializer.data

        self.assertEqual(data['name'], 'Router-01')
        self.assertEqual(data['serial_number'], 'SN123456')
        self.assertEqual(data['site_name'], 'DataCenter1')
        self.assertIn('id', data)

    def test_serialize_device_with_related_site(self):
        """Test Device serialization includes site_name."""
        serializer = DeviceSerializer(self.device)
        data = serializer.data

        self.assertEqual(data['site_name'], self.site.name)

    def test_deserialize_device(self):
        """Test Device deserialization."""
        data = {
            'name': 'Router-02',
            'site': self.site.id,
            'serial_number': 'SN654321'
        }
        serializer = DeviceSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        device = serializer.save()
        self.assertEqual(device.name, 'Router-02')

    def test_device_required_fields(self):
        """Test required fields validation."""
        data = {'name': 'Router-03'}
        serializer = DeviceSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('site', serializer.errors)


class InterfaceSerializerTests(TestCase):
    """Test cases for InterfaceSerializer."""

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

    def test_serialize_interface(self):
        """Test Interface serialization."""
        serializer = InterfaceSerializer(self.interface)
        data = serializer.data

        self.assertEqual(data['name'], 'eth0')
        self.assertEqual(data['speed'], 1000)
        self.assertEqual(data['status'], 'Up')
        self.assertEqual(data['device_name'], 'Router-01')
        self.assertIn('id', data)

    def test_serialize_interface_with_related_device(self):
        """Test Interface serialization includes device_name."""
        serializer = InterfaceSerializer(self.interface)
        data = serializer.data

        self.assertEqual(data['device_name'], self.device.name)

    def test_deserialize_interface(self):
        """Test Interface deserialization."""
        data = {
            'name': 'eth1',
            'device': self.device.id,
            'speed': 100,
            'status': 'Down'
        }
        serializer = InterfaceSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        interface = serializer.save()
        self.assertEqual(interface.name, 'eth1')
        self.assertEqual(interface.speed, 100)

    def test_interface_required_fields(self):
        """Test required fields validation."""
        data = {'name': 'eth5'}
        serializer = InterfaceSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('device', serializer.errors)
        self.assertIn('speed', serializer.errors)


class ConnectionSerializerTests(APITestCase):
    """Test cases for ConnectionSerializer."""

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
            speed=1000,
            status='Up'
        )
        self.interface2 = Interface.objects.create(
            name='eth0',
            device=self.device2,
            speed=1000,
            status='Up'
        )
        self.connection = Connection.objects.create(
            connection_id='CONN001',
            name='Link1',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )

    def test_serialize_connection(self):
        """Test Connection serialization."""
        serializer = ConnectionSerializer(self.connection)
        data = serializer.data

        self.assertEqual(data['connection_id'], 'CONN001')
        self.assertEqual(data['name'], 'Link1')
        self.assertEqual(data['status'], 'Connected')
        self.assertIn('id', data)
        self.assertIn('start_target', data)
        self.assertIn('end_target', data)

    def test_serialize_connection_start_target(self):
        """Test Connection serialization includes start_target."""
        serializer = ConnectionSerializer(self.connection)
        data = serializer.data

        start_target = data['start_target']
        self.assertIn('site', start_target)
        self.assertIn('device', start_target)
        self.assertIn('interface', start_target)
        self.assertEqual(start_target['device']['name'], 'Router-01')
        self.assertEqual(start_target['interface']['name'], 'eth0')

    def test_serialize_connection_end_target(self):
        """Test Connection serialization includes end_target."""
        serializer = ConnectionSerializer(self.connection)
        data = serializer.data

        end_target = data['end_target']
        self.assertIn('site', end_target)
        self.assertIn('device', end_target)
        self.assertIn('interface', end_target)
        self.assertEqual(end_target['device']['name'], 'Router-02')
        self.assertEqual(end_target['interface']['name'], 'eth0')

    def test_deserialize_connection(self):
        """Test Connection deserialization."""
        data = {
            'connection_id': 'CONN002',
            'name': 'Link2',
            'status': 'Disconnected',
            'start_interface': self.interface1.id,
            'end_interface': self.interface2.id
        }
        serializer = ConnectionSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        connection = serializer.save()
        self.assertEqual(connection.connection_id, 'CONN002')
        self.assertEqual(connection.status, 'Disconnected')

    def test_connection_create_method(self):
        """Test Connection create method."""
        data = {
            'connection_id': 'CONN003',
            'name': 'Link3',
            'status': 'Connected',
            'start_interface': self.interface1.id,
            'end_interface': self.interface2.id
        }
        serializer = ConnectionSerializer(data=data)
        serializer.is_valid()
        connection = serializer.save()

        self.assertIsNotNone(connection.id)
        self.assertEqual(connection.connection_id, 'CONN003')

    def test_connection_update_method(self):
        """Test Connection update method."""
        data = {
            'connection_id': 'CONN001',
            'name': 'Updated Link1',
            'status': 'Disconnected'
        }
        serializer = ConnectionSerializer(
            self.connection,
            data=data,
            partial=True
        )
        serializer.is_valid()
        connection = serializer.save()

        self.assertEqual(connection.name, 'Updated Link1')
        self.assertEqual(connection.status, 'Disconnected')

    def test_connection_required_fields(self):
        """Test required fields validation."""
        data = {'name': 'Link'}
        serializer = ConnectionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('connection_id', serializer.errors)
        self.assertIn('start_interface', serializer.errors)
        self.assertIn('end_interface', serializer.errors)
