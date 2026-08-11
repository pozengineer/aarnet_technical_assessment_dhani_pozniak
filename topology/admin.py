"""
Django admin customization for topology app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Connection, Device, Interface, Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    """Admin interface for Site model."""

    ordering = ['id']
    list_display = ['name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'status')
        }),
        (_('Important dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name',
                'description',
                'status',
            )
        }),
    )


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin interface for Device model."""

    ordering = ['id']
    list_display = ['name', 'site', 'serial_number', 'created_at']
    list_filter = ['site', 'created_at']
    search_fields = ['name', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('name', 'site', 'serial_number')
        }),
        (_('Important dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name',
                'site',
                'serial_number',
            )
        }),
    )


@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    """Admin interface for Interface model."""

    ordering = ['id']
    list_display = ['name', 'device', 'speed', 'status', 'created_at']
    list_filter = ['status', 'device', 'created_at']
    search_fields = ['name', 'device__name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('name', 'device', 'speed', 'status')
        }),
        (_('Important dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name',
                'device',
                'speed',
                'status',
            )
        }),
    )


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    """Admin interface for Connection model."""

    ordering = ['id']
    list_display = ['connection_id', 'name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['connection_id', 'name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('connection_id', 'name', 'status')
        }),
        (_('Interfaces'), {
            'fields': ('start_interface', 'end_interface')
        }),
        (_('Important dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'connection_id',
                'name',
                'status',
                'start_interface',
                'end_interface',
            )
        }),
    )
