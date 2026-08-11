"""
Unit tests for topology models.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from topology.models import Connection, Device, Interface, Site


class SiteModelTests(TestCase):
    """Test cases for Site model."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(
            name='London',
            description='Primary data center',
            status='Active'
        )

    def test_site_creation(self):
        """Test Site creation."""
        self.assertEqual(self.site.name, 'London')
        self.assertEqual(self.site.description, 'Primary data center')
        self.assertEqual(self.site.status, 'Active')

    def test_site_str_representation(self):
        """Test Site string representation."""
        self.assertEqual(str(self.site), 'London')

    def test_site_unique_name(self):
        """Test that site names must be unique."""
        with self.assertRaises(Exception):
            Site.objects.create(name='London', status='Active')

    def test_site_status_choices(self):
        """Test all valid status choices."""
        statuses = ['Active', 'Planned', 'Decommissioned']
        for status in statuses:
            site = Site.objects.create(name=f'Site_{status}', status=status)
            self.assertEqual(site.status, status)

    def test_site_default_status(self):
        """Test default status is Active."""
        site = Site.objects.create(name='Tokyo')
        self.assertEqual(site.status, 'Active')

    def test_site_description_optional(self):
        """Test that description is optional."""
        site = Site.objects.create(name='Paris')
        self.assertIsNone(site.description)

    def test_site_timestamps(self):
        """Test created_at and updated_at timestamps."""
        self.assertIsNotNone(self.site.created_at)
        self.assertIsNotNone(self.site.updated_at)

    def test_site_ordering(self):
        """Test sites are ordered by name."""
        Site.objects.create(name='Berlin', status='Active')
        Site.objects.create(name='Amsterdam', status='Active')

        sites = list(Site.objects.all())
        self.assertEqual(sites[0].name, 'Amsterdam')
        self.assertEqual(sites[1].name, 'Berlin')


class DeviceModelTests(TestCase):
    """Test cases for Device model."""

    def setUp(self):
        """Set up test fixtures."""
        self.site = Site.objects.create(name='DataCenter1', status='Active')
        self.device = Device.objects.create(
            name='Router-01',
            site=self.site,
            serial_number='SN123456'
        )

    def test_device_creation(self):
        """Test Device creation."""
        self.assertEqual(self.device.name, 'Router-01')
        self.assertEqual(self.device.site, self.site)
        self.assertEqual(self.device.serial_number, 'SN123456')

    def test_device_str_representation(self):
        """Test Device string representation."""
        self.assertEqual(str(self.device), 'Router-01')

    def test_device_site_relationship(self):
        """Test Device-Site foreign key relationship."""
        self.assertEqual(self.device.site.id, self.site.id)

    def test_device_unique_name(self):
        """Test that device names must be unique."""
        with self.assertRaises(Exception):
            Device.objects.create(
                name='Router-01',
                site=self.site,
                serial_number='SN999999'
            )

    def test_device_unique_serial_number(self):
        """Test that serial numbers must be unique."""
        with self.assertRaises(Exception):
            Device.objects.create(
                name='Router-02',
                site=self.site,
                serial_number='SN123456'
            )

    def test_device_cascade_delete_with_site(self):
        """Test that deleting a site cascades to devices."""
        device_id = self.device.id
        self.site.delete()

        with self.assertRaises(Device.DoesNotExist):
            Device.objects.get(id=device_id)

    def test_device_ordering(self):
        """Test devices are ordered by name."""
        Device.objects.create(
            name='Switch-01',
            site=self.site,
            serial_number='SN111111'
        )
        Device.objects.create(
            name='Firewall-01',
            site=self.site,
            serial_number='SN222222'
        )

        devices = list(Device.objects.all())
        self.assertEqual(devices[0].name, 'Firewall-01')
        self.assertEqual(devices[1].name, 'Router-01')
        self.assertEqual(devices[2].name, 'Switch-01')

    def test_device_timestamps(self):
        """Test created_at and updated_at timestamps."""
        self.assertIsNotNone(self.device.created_at)
        self.assertIsNotNone(self.device.updated_at)


class InterfaceModelTests(TestCase):
    """Test cases for Interface model."""

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

    def test_interface_creation(self):
        """Test Interface creation."""
        self.assertEqual(self.interface.name, 'eth0')
        self.assertEqual(self.interface.device, self.device)
        self.assertEqual(self.interface.speed, 1000)
        self.assertEqual(self.interface.status, 'Up')

    def test_interface_str_representation(self):
        """Test Interface string representation."""
        self.assertEqual(str(self.interface), 'Router-01/eth0')

    def test_interface_device_relationship(self):
        """Test Interface-Device foreign key relationship."""
        self.assertEqual(self.interface.device.id, self.device.id)

    def test_interface_status_choices(self):
        """Test all valid status choices."""
        statuses = ['Down', 'Maintenance']
        for i, status in enumerate(statuses, start=1):
            interface = Interface.objects.create(
                name=f'eth{i}',
                device=self.device,
                speed=1000,
                status=status
            )
            self.assertEqual(interface.status, status)

    def test_interface_default_status(self):
        """Test default status is Down."""
        interface = Interface.objects.create(
            name='eth99',
            device=self.device,
            speed=100
        )
        self.assertEqual(interface.status, 'Down')

    def test_interface_unique_together_name_device(self):
        """Test that name+device combination must be unique."""
        with self.assertRaises(Exception):
            Interface.objects.create(
                name='eth0',
                device=self.device,
                speed=1000
            )

    def test_interface_same_name_different_device_allowed(self):
        """Test that same interface name is allowed on different devices."""
        device2 = Device.objects.create(
            name='Router-02',
            site=self.site,
            serial_number='SN654321'
        )
        interface2 = Interface.objects.create(
            name='eth0',
            device=device2,
            speed=1000
        )
        self.assertNotEqual(interface2.id, self.interface.id)

    def test_interface_cascade_delete_with_device(self):
        """Test that deleting a device cascades to interfaces."""
        interface_id = self.interface.id
        self.device.delete()

        with self.assertRaises(Interface.DoesNotExist):
            Interface.objects.get(id=interface_id)

    def test_interface_ordering(self):
        """Test interfaces are ordered by device then name."""
        Interface.objects.create(
            name='eth1',
            device=self.device,
            speed=100
        )
        Interface.objects.create(
            name='eth2',
            device=self.device,
            speed=10
        )

        interfaces = list(Interface.objects.all())
        self.assertEqual(interfaces[0].name, 'eth0')
        self.assertEqual(interfaces[1].name, 'eth1')
        self.assertEqual(interfaces[2].name, 'eth2')

    def test_interface_timestamps(self):
        """Test created_at and updated_at timestamps."""
        self.assertIsNotNone(self.interface.created_at)
        self.assertIsNotNone(self.interface.updated_at)


class ConnectionModelTests(TestCase):
    """Test cases for Connection model."""

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

    def test_connection_creation(self):
        """Test Connection creation."""
        self.assertEqual(self.connection.connection_id, 'CONN001')
        self.assertEqual(self.connection.name, 'Link1')
        self.assertEqual(self.connection.status, 'Connected')

    def test_connection_str_representation(self):
        """Test Connection string representation."""
        self.assertEqual(str(self.connection), 'CONN001: Link1')

    def test_connection_str_unnamed(self):
        """Test Connection string representation when unnamed."""
        connection = Connection.objects.create(
            connection_id='CONN002',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )
        self.assertEqual(str(connection), 'CONN002: Unnamed')

    def test_connection_interface_relationship(self):
        """Test Connection-Interface foreign key relationships."""
        self.assertEqual(self.connection.start_interface.id, self.interface1.id)
        self.assertEqual(self.connection.end_interface.id, self.interface2.id)

    def test_connection_status_choices(self):
        """Test all valid status choices."""
        statuses = ['Disconnected']
        for i, status in enumerate(statuses, start=2):
            interface_a = Interface.objects.create(
                name=f'eth{i}a',
                device=self.device1,
                speed=1000
            )
            interface_b = Interface.objects.create(
                name=f'eth{i}b',
                device=self.device2,
                speed=1000
            )
            connection = Connection.objects.create(
                connection_id=f'CONN{i:03d}',
                status=status,
                start_interface=interface_a,
                end_interface=interface_b
            )
            self.assertEqual(connection.status, status)

    def test_connection_default_status(self):
        """Test default status is Connected."""
        connection = Connection.objects.create(
            connection_id='CONN999',
            start_interface=self.interface1,
            end_interface=self.interface2
        )
        self.assertEqual(connection.status, 'Connected')

    def test_connection_unique_id(self):
        """Test that connection IDs must be unique."""
        with self.assertRaises(Exception):
            Connection.objects.create(
                connection_id='CONN001',
                status='Connected',
                start_interface=self.interface1,
                end_interface=self.interface2
            )

    def test_connection_name_optional(self):
        """Test that name is optional."""
        connection = Connection.objects.create(
            connection_id='CONN777',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )
        self.assertIsNone(connection.name)

    def test_connection_clean_same_interface_validation(self):
        """Test validation prevents connecting interface to itself."""
        connection = Connection(
            connection_id='CONN555',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface1
        )
        with self.assertRaises(ValidationError):
            connection.full_clean()

    def test_connection_cascade_delete_with_interface(self):
        """Test that deleting an interface cascades to connections."""
        connection_id = self.connection.id
        self.interface1.delete()

        with self.assertRaises(Connection.DoesNotExist):
            Connection.objects.get(id=connection_id)

    def test_connection_ordering(self):
        """Test connections are ordered by connection_id."""
        Connection.objects.create(
            connection_id='CONN_A',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )
        Connection.objects.create(
            connection_id='CONN_B',
            status='Connected',
            start_interface=self.interface1,
            end_interface=self.interface2
        )

        connections = list(Connection.objects.all())
        self.assertEqual(connections[0].connection_id, 'CONN001')
        self.assertEqual(connections[1].connection_id, 'CONN_A')
        self.assertEqual(connections[2].connection_id, 'CONN_B')

    def test_connection_timestamps(self):
        """Test created_at and updated_at timestamps."""
        self.assertIsNotNone(self.connection.created_at)
        self.assertIsNotNone(self.connection.updated_at)
