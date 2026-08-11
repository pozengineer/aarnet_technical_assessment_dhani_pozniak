"""
Serializers for network topology API.
"""

from rest_framework import serializers
from .models import Site, Device, Interface, Connection


class SiteSerializer(serializers.ModelSerializer):
    """Serializer for Site model."""

    class Meta:
        model = Site
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model."""

    site_name = serializers.CharField(source='site.name', read_only=True)

    class Meta:
        model = Device
        fields = ['id', 'name', 'site', 'site_name', 'serial_number', 'created_at', 'updated_at']


class InterfaceSerializer(serializers.ModelSerializer):
    """Serializer for Interface model."""

    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = Interface
        fields = ['id', 'name', 'device', 'device_name', 'speed', 'status', 'created_at', 'updated_at']


class ConnectionTargetSerializer(serializers.Serializer):
    """Serializer for connection endpoint targets (site, device, interface tuple)."""

    site = SiteSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    interface = InterfaceSerializer(read_only=True)


class ConnectionSerializer(serializers.ModelSerializer):
    """Serializer for Connection model."""

    start_target = serializers.SerializerMethodField()
    end_target = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = [
            'id', 'connection_id', 'name', 'status',
            'start_interface', 'start_target',
            'end_interface', 'end_target',
            'created_at', 'updated_at'
        ]

    def get_start_target(self, obj):
        """Get the complete start target with site, device, interface."""
        interface = obj.start_interface
        return {
            'site': SiteSerializer(interface.device.site).data,
            'device': DeviceSerializer(interface.device).data,
            'interface': InterfaceSerializer(interface).data,
        }

    def get_end_target(self, obj):
        """Get the complete end target with site, device, interface."""
        interface = obj.end_interface
        return {
            'site': SiteSerializer(interface.device.site).data,
            'device': DeviceSerializer(interface.device).data,
            'interface': InterfaceSerializer(interface).data,
        }

    def create(self, validated_data):
        """Create a connection instance."""
        return Connection.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update a connection instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
