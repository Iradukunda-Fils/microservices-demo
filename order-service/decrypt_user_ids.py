#!/usr/bin/env python
"""
Script to decrypt existing user_id values in orders
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')
django.setup()

from orders.models import Order
from encrypted_model_fields.fields import EncryptedCharField
from cryptography.fernet import Fernet
from django.conf import settings

print("Decrypting user_id values...")

# Get the encryption key
key = settings.FIELD_ENCRYPTION_KEY.encode() if isinstance(settings.FIELD_ENCRYPTION_KEY, str) else settings.FIELD_ENCRYPTION_KEY
cipher = Fernet(key)

# Get all orders
orders = Order.objects.all()
print(f"Found {orders.count()} orders")

decrypted_count = 0
for order in orders:
    # Get the raw encrypted value from database
    raw_value = order.user_id
    
    # Check if it looks encrypted (starts with gAAAAA)
    if raw_value and raw_value.startswith('gAAAAA'):
        try:
            # Decrypt it
            decrypted = cipher.decrypt(raw_value.encode()).decode()
            # Update with decrypted value
            Order.objects.filter(id=order.id).update(user_id=decrypted)
            decrypted_count += 1
            print(f"Order {order.id}: Decrypted user_id to '{decrypted}'")
        except Exception as e:
            print(f"Order {order.id}: Failed to decrypt - {e}")
    else:
        print(f"Order {order.id}: Already decrypted (user_id='{raw_value}')")

print(f"\nDecrypted {decrypted_count} orders")
print("Done!")
