"""
Product models for ProductService.

Educational Note: This demonstrates service-specific data models.
Each service owns its data and provides APIs for other services to access it.
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    """
    Product model representing items in the catalog.
    
    Educational Note: This model is owned by ProductService.
    Other services (like OrderService) reference products by ID,
    but never access this database directly.
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Product name"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Product description"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Product price (must be positive)"
    )
    
    inventory_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Available inventory (must be non-negative)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the product was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the product was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} (${self.price})"
    
    @property
    def is_available(self):
        """
        Check if product is available for purchase.
        
        Educational Note: This is a computed property, not stored in database.
        """
        return self.inventory_count > 0
    
    def check_availability(self, quantity):
        """
        Check if sufficient inventory exists for the requested quantity.
        
        Educational Note: This method is called via gRPC by OrderService
        before creating orders.
        
        Args:
            quantity: Requested quantity
        
        Returns:
            bool: True if sufficient inventory exists
        """
        return self.inventory_count >= quantity
    
    def reserve_inventory(self, quantity):
        """
        Reserve inventory for an order.
        
        Educational Note: In production, this should be part of a
        distributed transaction or saga pattern to ensure consistency.
        
        Args:
            quantity: Quantity to reserve
        
        Raises:
            ValueError: If insufficient inventory
        """
        if not self.check_availability(quantity):
            raise ValueError(f"Insufficient inventory. Available: {self.inventory_count}, Requested: {quantity}")
        
        self.inventory_count -= quantity
        self.save()
