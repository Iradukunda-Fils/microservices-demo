"""
Factory classes for generating order test data.

Educational Note: Order factories are more complex because they involve:
- Relationships (Order -> OrderItem)
- Cross-service references (user_id, product_id)
- Calculated fields (total_amount)
- Business logic (inventory checking)
"""

import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
import random
from .models import Order, OrderItem


class OrderFactory(DjangoModelFactory):
    """
    Factory for creating Order instances.
    
    Educational Note: This factory demonstrates:
    - String user_id (references UserService)
    - Calculated total_amount
    - Status choices
    - Encrypted fields (user_id is encrypted automatically)
    """
    
    class Meta:
        model = Order
    
    # Educational Note: user_id is a string that references UserService
    # It will be encrypted automatically by django-encrypted-model-fields
    user_id = factory.Sequence(lambda n: str(n % 10 + 1))  # Users 1-10
    
    # Default to pending status
    status = 'pending'
    
    # Total amount will be calculated from order items
    # We set a default here, but it should be recalculated after adding items
    total_amount = Decimal('0.00')


class OrderItemFactory(DjangoModelFactory):
    """
    Factory for creating OrderItem instances.
    
    Educational Note: This factory demonstrates:
    - ForeignKey relationships (order)
    - Cross-service references (product_id)
    - Price snapshots (price_at_purchase)
    - Quantity handling
    """
    
    class Meta:
        model = OrderItem
    
    # Will be set by parent factory or explicitly
    order = factory.SubFactory(OrderFactory)
    
    # Educational Note: product_id is a string that references ProductService
    # We use products 1-20 (assuming they exist from seeding)
    product_id = factory.LazyFunction(lambda: str(random.randint(1, 20)))
    
    # Random quantity between 1 and 5
    quantity = factory.LazyFunction(lambda: random.randint(1, 5))
    
    # Random price between $10 and $500
    # Educational Note: This is the price at time of purchase
    # In a real system, you'd fetch this from ProductService
    price_at_purchase = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(10.00, 500.00), 2)))
    )


class CompleteOrderFactory(OrderFactory):
    """
    Factory for creating complete orders with items.
    
    Educational Note: This demonstrates the post_generation hook
    which allows creating related objects after the main object is created.
    """
    
    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        """
        Create order items after order is created.
        
        Args:
            create: Whether to save to database
            extracted: Explicitly passed items
            **kwargs: Additional arguments
            
        Educational Note: post_generation hooks run after object creation.
        This is perfect for creating related objects and updating calculated fields.
        """
        if not create:
            # Build strategy, not create
            return
        
        if extracted:
            # Use explicitly provided items
            for item_data in extracted:
                OrderItem.objects.create(order=self, **item_data)
        else:
            # Create random number of items (1-5)
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                OrderItemFactory.create(order=self)
        
        # Recalculate total amount
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()


class PendingOrderFactory(CompleteOrderFactory):
    """Factory for creating orders in pending status."""
    status = 'pending'


class ConfirmedOrderFactory(CompleteOrderFactory):
    """Factory for creating orders in confirmed status."""
    status = 'confirmed'


class ShippedOrderFactory(CompleteOrderFactory):
    """Factory for creating orders in shipped status."""
    status = 'shipped'


class DeliveredOrderFactory(CompleteOrderFactory):
    """Factory for creating orders in delivered status."""
    status = 'delivered'
