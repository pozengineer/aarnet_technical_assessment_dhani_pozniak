"""
Models for network topology tracking.
"""

from django.core.exceptions import ValidationError
from django.db import models


class Site(models.Model):
    """Represents a physical location or data center."""

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Planned', 'Planned'),
        ('Decommissioned', 'Decommissioned'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Device(models.Model):
    """Represents a network device (router, switch, etc.)."""

    name = models.CharField(max_length=255, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='devices')
    serial_number = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Interface(models.Model):
    """Represents a network interface on a device."""

    STATUS_CHOICES = [
        ('Up', 'Up'),
        ('Down', 'Down'),
        ('Maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=255)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='interfaces')
    speed = models.IntegerField(help_text='Speed in Mbps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Down')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'device')
        ordering = ['device', 'name']

    def __str__(self):
        return f"{self.device.name}/{self.name}"


class Connection(models.Model):
    """Represents a point-to-point connection between two interfaces."""

    STATUS_CHOICES = [
        ('Connected', 'Connected'),
        ('Disconnected', 'Disconnected'),
    ]

    connection_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Connected')

    # Start interface reference
    start_interface = models.ForeignKey(
        Interface,
        on_delete=models.CASCADE,
        related_name='connections_as_start'
    )

    # End interface reference
    end_interface = models.ForeignKey(
        Interface,
        on_delete=models.CASCADE,
        related_name='connections_as_end'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['connection_id']

    def __str__(self):
        return f"{self.connection_id}: {self.name or 'Unnamed'}"

    def clean(self):
        """Ensure start and end interfaces are different."""
        if self.start_interface_id and self.end_interface_id:
            if self.start_interface_id == self.end_interface_id:
                raise ValidationError('Start and end interfaces must be different.')
