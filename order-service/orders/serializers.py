"""
DRF serializers for Order models.

Educational Note: Serializers in Django REST Framework:
- Convert complex data types (models) to Python datatypes (JSON)
- Provide validation for incoming data
- Handle deserialization (JSON -> model instances)
- Similar to forms but designed for APIs
"""

from rest_framework import serializers
from .models import Order, OrderItem
from decimal import Decimal


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    
    Educational Note: We include a computed field (subtotal) that's not
    stored in the database but calculated on-the-fly.
    """
    
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text="Calculated as quantity * price_at_purchase"
    )
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity', 'price_at_purchase', 'subtotal']
        read_only_fields = ['id', 'price_at_purchase', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model with nested order items.
    
    Educational Note: This demonstrates nested serialization.
    The 'items' field will include full OrderItem data in the response.
    """
    
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_amount', 'status', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating orders.
    
    Educational Note: This is a custom serializer (not ModelSerializer) because
    order creation involves complex validation across multiple services:
    1. Get user from JWT token (request.user)
    2. Validate products exist (call ProductService via gRPC)
    3. Check inventory availability (call ProductService via gRPC)
    4. Calculate total amount
    5. Create Order and OrderItem records
    
    This demonstrates the orchestration pattern in microservices.
    Security: user_id comes from authenticated JWT token, not client input.
    """
    
    items = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        min_length=1,
        help_text="List of order items with product_id and quantity"
    )
    
    def validate_items(self, value):
        """
        Validate order items structure.
        
        Educational Note: Custom validation in DRF serializers.
        This runs before the main validation logic.
        """
        for item in value:
            if 'product_id' not in item:
                raise serializers.ValidationError("Each item must have a product_id")
            if 'quantity' not in item:
                raise serializers.ValidationError("Each item must have a quantity")
            
            # Validate types
            try:
                product_id = int(item['product_id'])
                if product_id <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                raise serializers.ValidationError("product_id must be a positive integer")
            
            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                raise serializers.ValidationError("quantity must be a positive integer")
        
        return value


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for order lists with nested items.
    
    Educational Note: We include nested items in the list view so the frontend
    can display order details without making additional API calls. This is a
    trade-off between response size and number of requests.
    """
    
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'total_amount', 'status', 'items', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'total_amount', 'status', 'items', 'item_count', 'created_at', 'updated_at']
    
    def get_item_count(self, obj):
        """Get count of items in the order."""
        return obj.items.count()
