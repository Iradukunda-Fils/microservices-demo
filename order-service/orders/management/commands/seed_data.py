"""
Management command to seed the database with sample order data.

Educational Note: Order seeding is more complex because:
- Orders reference users from UserService
- OrderItems reference products from ProductService
- We need to ensure referenced entities exist
- Total amounts must be calculated correctly

Usage: python manage.py seed_data [--orders 30] [--clear]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from orders.factories import (
    CompleteOrderFactory,
    PendingOrderFactory,
    ConfirmedOrderFactory,
    ShippedOrderFactory,
    DeliveredOrderFactory,
)
from orders.models import Order, OrderItem
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed the database with sample order data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--orders',
            type=int,
            default=30,
            help='Number of orders to create (default: 30)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        num_orders = options['orders']
        clear_data = options['clear']
        
        self.stdout.write(self.style.WARNING('🌱 Starting order database seeding...'))
        
        try:
            with transaction.atomic():
                # Clear existing data if requested
                if clear_data:
                    self.stdout.write('🗑️  Clearing existing orders...')
                    Order.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS('✅ Orders cleared'))
                
                # Check if data already exists
                if Order.objects.exists() and not clear_data:
                    self.stdout.write(
                        self.style.WARNING(
                            '⚠️  Database already contains orders. Use --clear to reset.'
                        )
                    )
                    return
                
                # Educational Note: We create orders in different statuses
                # to simulate a realistic order lifecycle
                
                # Calculate distribution
                pending_count = int(num_orders * 0.3)  # 30% pending
                confirmed_count = int(num_orders * 0.2)  # 20% confirmed
                shipped_count = int(num_orders * 0.2)  # 20% shipped
                delivered_count = num_orders - pending_count - confirmed_count - shipped_count  # Rest delivered
                
                # Create pending orders
                self.stdout.write(f'📦 Creating {pending_count} pending orders...')
                pending_orders = PendingOrderFactory.create_batch(pending_count)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(pending_orders)} pending orders')
                )
                
                # Create confirmed orders
                self.stdout.write(f'✅ Creating {confirmed_count} confirmed orders...')
                confirmed_orders = ConfirmedOrderFactory.create_batch(confirmed_count)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(confirmed_orders)} confirmed orders')
                )
                
                # Create shipped orders
                self.stdout.write(f'🚚 Creating {shipped_count} shipped orders...')
                shipped_orders = ShippedOrderFactory.create_batch(shipped_count)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(shipped_orders)} shipped orders')
                )
                
                # Create delivered orders
                self.stdout.write(f'📬 Creating {delivered_count} delivered orders...')
                delivered_orders = DeliveredOrderFactory.create_batch(delivered_count)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(delivered_orders)} delivered orders')
                )
                
                # Summary
                total_orders = Order.objects.count()
                total_items = OrderItem.objects.count()
                
                # Status breakdown
                status_counts = {}
                for status_code, status_name in Order.STATUS_CHOICES:
                    count = Order.objects.filter(status=status_code).count()
                    status_counts[status_name] = count
                
                # Calculate total revenue
                from decimal import Decimal
                total_revenue = sum(
                    order.total_amount for order in Order.objects.all()
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🎉 Order database seeding complete!'
                    )
                )
                self.stdout.write(f'   Total orders: {total_orders}')
                self.stdout.write(f'   Total order items: {total_items}')
                self.stdout.write(f'   Total revenue: ${total_revenue:,.2f}')
                
                self.stdout.write('\n📊 Orders by status:')
                for status_name, count in status_counts.items():
                    if count > 0:
                        self.stdout.write(f'   {status_name}: {count}')
                
                # Show sample orders
                self.stdout.write('\n📝 Sample orders:')
                for order in Order.objects.all()[:5]:
                    item_count = order.items.count()
                    self.stdout.write(
                        f'   Order #{order.id} - User {order.user_id} - '
                        f'${order.total_amount} - {order.status} - {item_count} items'
                    )
                
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  Note: Orders reference users (1-10) and products (1-20).'
                    )
                )
                self.stdout.write(
                    '   Make sure UserService and ProductService are seeded first!'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error seeding database: {e}')
            )
            logger.error(f'Order database seeding failed: {e}', exc_info=True)
            raise
