"""
Admin configuration for products app.

Educational Note: Django admin provides a ready-to-use admin interface.
"""

from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model.
    
    Educational Note: Customize the admin interface for better usability.
    """
    
    list_display = ['id', 'name', 'price', 'inventory_count', 'is_available', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'price')
        }),
        ('Inventory', {
            'fields': ('inventory_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
