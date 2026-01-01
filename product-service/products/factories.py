"""
Factory classes for generating product test data.

Educational Note: This demonstrates how to create realistic product data
with proper pricing, inventory, and descriptions.
"""

import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
import random
from .models import Product


class ProductFactory(DjangoModelFactory):
    """
    Factory for creating Product instances with realistic tech product data.
    
    Educational Note: This factory demonstrates:
    - Using factory.Faker for realistic data
    - LazyAttribute for computed values
    - Decimal handling for prices
    - Random choices for variety
    """
    
    class Meta:
        model = Product
    
    # Educational Note: We use predefined tech products for realism
    # In production, you might use factory.Faker('word') for random names
    name = factory.Iterator([
        'Wireless Mouse',
        'Mechanical Keyboard',
        '27" 4K Monitor',
        'USB-C Hub',
        'Laptop Stand',
        'Webcam HD',
        'Noise-Cancelling Headphones',
        'External SSD 1TB',
        'Ergonomic Chair',
        'Standing Desk',
        'Graphics Tablet',
        'Microphone USB',
        'LED Desk Lamp',
        'Cable Management Kit',
        'Laptop Backpack',
    ])
    
    # LazyAttribute generates value based on other attributes
    description = factory.LazyAttribute(
        lambda obj: f'High-quality {obj.name.lower()} for professionals and enthusiasts. '
                   f'Perfect for your home office or workspace.'
    )
    
    # Random prices between $19.99 and $999.99
    price = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(19.99, 999.99), 2)))
    )
    
    # Random inventory between 0 and 100
    inventory_count = factory.LazyFunction(
        lambda: random.randint(0, 100)
    )


class LaptopFactory(ProductFactory):
    """Factory for creating laptop products with higher prices."""
    
    name = factory.Iterator([
        'MacBook Pro 16"',
        'Dell XPS 15',
        'ThinkPad X1 Carbon',
        'HP Spectre x360',
        'ASUS ROG Gaming Laptop',
    ])
    
    description = factory.LazyAttribute(
        lambda obj: f'{obj.name} - Professional laptop with high performance, '
                   f'long battery life, and premium build quality.'
    )
    
    # Laptops are more expensive
    price = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(999.99, 2999.99), 2)))
    )
    
    # Lower inventory for expensive items
    inventory_count = factory.LazyFunction(
        lambda: random.randint(5, 30)
    )


class AccessoryFactory(ProductFactory):
    """Factory for creating accessory products with lower prices."""
    
    name = factory.Iterator([
        'USB Cable 6ft',
        'Mouse Pad',
        'Screen Cleaner',
        'Cable Clips',
        'Desk Organizer',
    ])
    
    description = factory.LazyAttribute(
        lambda obj: f'{obj.name} - Essential accessory for your workspace.'
    )
    
    # Accessories are cheaper
    price = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(5.99, 49.99), 2)))
    )
    
    # Higher inventory for cheap items
    inventory_count = factory.LazyFunction(
        lambda: random.randint(50, 200)
    )


class OutOfStockProductFactory(ProductFactory):
    """Factory for creating out-of-stock products (for testing)."""
    
    inventory_count = 0
