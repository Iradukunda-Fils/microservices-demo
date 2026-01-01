#!/usr/bin/env python
"""Debug script to check order filtering issue."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')
django.setup()

from orders.models import Order

print("=" * 60)
print("DEBUG: Order Filtering Issue")
print("=" * 60)

# Get all orders
all_orders = Order.objects.all()
print(f"\n📊 Total orders in database: {all_orders.count()}")

# Check first few orders
for order in all_orders[:5]:
    print(f"\nOrder {order.id}:")
    print(f"  user_id (decrypted): {order.user_id}")
    print(f"  user_id type: {type(order.user_id)}")
    print(f"  user_id repr: {repr(order.user_id)}")
    print(f"  total_amount: {order.total_amount}")

# Try different filtering approaches
print("\n" + "=" * 60)
print("Testing different filter approaches:")
print("=" * 60)

test_user_ids = ["1", 1, "01", " 1", "1 "]

for test_id in test_user_ids:
    filtered = Order.objects.filter(user_id=test_id)
    print(f"\nFilter by {repr(test_id)} (type: {type(test_id).__name__}): {filtered.count()} orders")

# Check if encryption is working
print("\n" + "=" * 60)
print("Checking encryption:")
print("=" * 60)

first_order = all_orders.first()
if first_order:
    # Access the raw encrypted value
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM orders_order WHERE id = %s", [first_order.id])
        raw_value = cursor.fetchone()[0]
        print(f"\nRaw encrypted value in DB: {repr(raw_value)}")
        print(f"Decrypted value: {repr(first_order.user_id)}")
