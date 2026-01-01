"""
Serializers for ProductService.

Educational Note: DRF ModelSerializer automatically creates fields
based on the model, reducing boilerplate significantly.
"""

from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    
    Educational Note: This serializer handles:
    - Validation (price > 0, inventory >= 0)
    - Serialization (Python objects → JSON)
    - Deserialization (JSON → Python objects)
    - Computed fields (is_available)
    """
    
    is_available = serializers.BooleanField(
        read_only=True,
        help_text="Whether the product is in stock"
    )
    
    # Ensure inventory_count is always included and has a default
    inventory_count = serializers.IntegerField(
        default=10,
        min_value=0,
        help_text="Available inventory count"
    )
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'inventory_count',
            'is_available',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_available']
    
    def validate_price(self, value):
        """
        Validate that price is positive.
        
        Educational Note: Field-level validation method.
        Called automatically by DRF during validation.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_inventory_count(self, value):
        """
        Validate that inventory count is non-negative.
        """
        if value < 0:
            raise serializers.ValidationError("Inventory count cannot be negative")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product listings.
    
    Educational Note: Use different serializers for list vs detail views
    to optimize performance (less data transfer).
    """
    
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'inventory_count', 'is_available']
