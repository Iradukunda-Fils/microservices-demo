"""
Factory classes for generating test data using factory-boy.

Educational Note: factory-boy is a fixtures replacement library that:
- Generates realistic test data
- Handles model relationships automatically
- Supports sequences and random data
- Makes tests more maintainable

Used by: Mozilla, Instagram, Eventbrite, and many others
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.hashers import make_password
from .models import User


class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances with realistic data.
    
    Educational Note: This factory demonstrates:
    - Sequences for unique values (username, email)
    - Password hashing (not storing plaintext!)
    - Default values for common fields
    - Faker integration for realistic data
    """
    
    class Meta:
        model = User
    
    # Sequence ensures unique usernames: user1, user2, user3, etc.
    username = factory.Sequence(lambda n: f'user{n}')
    
    # Sequence with faker for realistic emails
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    
    # Educational Note: We hash passwords properly!
    # Never store plaintext passwords in the database
    password = factory.LazyFunction(lambda: make_password('password123'))
    
    # Default values
    is_active = True
    is_staff = False
    is_superuser = False


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin users.
    
    Educational Note: Inheritance in factory-boy.
    This factory extends UserFactory and overrides specific fields.
    """
    
    username = factory.Sequence(lambda n: f'admin{n}')
    email = factory.Sequence(lambda n: f'admin{n}@example.com')
    is_staff = True
    is_superuser = True


class StaffUserFactory(UserFactory):
    """Factory for creating staff users (not superuser)."""
    
    username = factory.Sequence(lambda n: f'staff{n}')
    email = factory.Sequence(lambda n: f'staff{n}@example.com')
    is_staff = True
    is_superuser = False
