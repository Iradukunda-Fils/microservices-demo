"""
Order models with field-level encryption for sensitive data.

Educational Note: This demonstrates several important patterns:
1. Field-level encryption using django-encrypted-model-fields
2. Proper model relationships (Order -> OrderItem)
3. Audit fields (created_at, updated_at)
4. Status tracking for order lifecycle
"""

from django.db import models


class Order(models.Model):
    """
    Order model representing a customer order.
    
    Educational Note: user_id is stored as a regular CharField.
    While encryption provides additional security, it prevents efficient
    database queries and filtering. For this demo, we prioritize functionality.
    
    In production, consider:
    - Encryption at rest (database level)
    - Access controls and audit logging
    - Data retention policies
    """
    
    # Regular CharField - allows efficient filtering
    user_id = models.CharField(max_length=255, db_index=True)
    
    # Order details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total order amount calculated from order items"
    )
    
    # Order status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current order status"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    """
    OrderItem model representing individual products in an order.
    
    Educational Note: This is a classic order-item relationship pattern.
    We store price_at_purchase to maintain historical accuracy even if
    product prices change later.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent order"
    )
    
    # Product reference (not a foreign key - different service!)
    # Educational Note: We store product_id as a string, not a ForeignKey,
    # because the Product model is in a different service (ProductService).
    # This is service isolation - no direct database relationships across services.
    product_id = models.CharField(
        max_length=255,
        help_text="Product ID from ProductService"
    )
    
    quantity = models.PositiveIntegerField(
        help_text="Quantity ordered"
    )
    
    # Price snapshot at time of purchase
    # Educational Note: We store the price at purchase time because:
    # 1. Product prices may change over time
    # 2. Orders should reflect the price the customer actually paid
    # 3. Historical accuracy for accounting and refunds
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price at time of purchase"
    )
    
    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"OrderItem {self.id} - Product {self.product_id} x{self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this order item."""
        return self.quantity * self.price_at_purchase
