"""
Management command to seed the database with sample product data.

Usage: python manage.py seed_data [--products 20] [--clear]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from products.factories import (
    ProductFactory,
    LaptopFactory,
    AccessoryFactory,
    OutOfStockProductFactory,
)
from products.models import Product
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed the database with sample product data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=20,
            help='Number of products to create (default: 20)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        num_products = options['products']
        clear_data = options['clear']
        
        self.stdout.write(self.style.WARNING('🌱 Starting product database seeding...'))
        
        try:
            with transaction.atomic():
                # Clear existing data if requested
                if clear_data:
                    self.stdout.write('🗑️  Clearing existing products...')
                    Product.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS('✅ Products cleared'))
                
                # Check if data already exists
                if Product.objects.exists() and not clear_data:
                    self.stdout.write(
                        self.style.WARNING(
                            '⚠️  Database already contains products. Use --clear to reset.'
                        )
                    )
                    return
                
                # Create a mix of products
                self.stdout.write('💻 Creating laptop products...')
                laptops = LaptopFactory.create_batch(5)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(laptops)} laptops')
                )
                
                self.stdout.write('🖱️  Creating accessory products...')
                accessories = AccessoryFactory.create_batch(5)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(accessories)} accessories')
                )
                
                self.stdout.write('📦 Creating general products...')
                remaining = num_products - 10 - 2  # Subtract laptops, accessories, and out-of-stock
                if remaining > 0:
                    products = ProductFactory.create_batch(remaining)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created {len(products)} general products')
                    )
                
                # Create a couple out-of-stock items for testing
                self.stdout.write('❌ Creating out-of-stock products (for testing)...')
                out_of_stock = OutOfStockProductFactory.create_batch(2)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {len(out_of_stock)} out-of-stock products')
                )
                
                # Summary
                total_products = Product.objects.count()
                in_stock = Product.objects.filter(inventory_count__gt=0).count()
                out_of_stock_count = Product.objects.filter(inventory_count=0).count()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🎉 Product database seeding complete!'
                    )
                )
                self.stdout.write(f'   Total products: {total_products}')
                self.stdout.write(f'   In stock: {in_stock}')
                self.stdout.write(f'   Out of stock: {out_of_stock_count}')
                
                # Show sample products
                self.stdout.write('\n📝 Sample products:')
                for product in Product.objects.all()[:5]:
                    self.stdout.write(
                        f'   {product.id}. {product.name} - ${product.price} '
                        f'(Stock: {product.inventory_count})'
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error seeding database: {e}')
            )
            logger.error(f'Product database seeding failed: {e}', exc_info=True)
            raise
