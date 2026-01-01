#!/usr/bin/env python
"""
Test script to debug user_id filtering issue
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')
django.setup()

from orders.models import Order

print("=" * 60)
print("DEBUGGING ORDER FILTERING ISSUE")
print("=" * 60)

# Get all orders
all_orders = Order.objects.all()
print(f"\n📊 Total orders in database: {all_orders.count()}")

if all_orders.exists():
    # Show first 3 orders
    for order in all_orders[:3]:
        print(f"\nOrder {order.id}:")
        print(f"  user_id (decrypted): {order.user_id}")
        print(f"  user_id type: {type(order.user_id)}")
        print(f"  user_id repr: {repr(order.user_id)}")
        print(f"  total_amount: {order.total_amount}")

# Test filtering with string "1"
print("\n" + "=" * 60)
print("TESTING FILTER WITH STRING '1'")
print("=" * 60)
filtered_str = Order.objects.filter(user_id="1")
print(f"Orders filtered by user_id='1': {filtered_str.count()}")

# Test filtering with int 1
print("\n" + "=" * 60)
print("TESTING FILTER WITH INT 1")
print("=" * 60)
filtered_int = Order.objects.filter(user_id=1)
print(f"Orders filtered by user_id=1: {filtered_int.count()}")

# Test exact match with actual value
if all_orders.exists():
    first_order = all_orders.first()
    actual_user_id = first_order.user_id
    print("\n" + "=" * 60)
    print(f"TESTING FILTER WITH ACTUAL VALUE: {repr(actual_user_id)}")
    print("=" * 60)
    filtered_actual = Order.objects.filter(user_id=actual_user_id)
    print(f"Orders filtered by user_id={repr(actual_user_id)}: {filtered_actual.count()}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
