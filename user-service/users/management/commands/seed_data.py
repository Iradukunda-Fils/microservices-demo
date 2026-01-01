"""
Management command to seed the database with sample data.

Educational Note: Django management commands are custom scripts that:
- Run via `python manage.py command_name`
- Have access to Django ORM and settings
- Can be run manually or in startup scripts
- Useful for data seeding, maintenance tasks, etc.

Usage: python manage.py seed_data [--users 10]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from users.factories import UserFactory, AdminUserFactory, StaffUserFactory
from users.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed the database with sample user data'
    
    def add_arguments(self, parser):
        """
        Add command-line arguments.
        
        Educational Note: argparse integration in Django commands.
        This allows customization of seeding behavior.
        """
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of regular users to create (default: 10)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        """
        Main command logic.
        
        Educational Note: Database transaction ensures atomicity.
        Either all data is created, or none is (no partial seeding).
        """
        num_users = options['users']
        clear_data = options['clear']
        
        self.stdout.write(self.style.WARNING('🌱 Starting database seeding...'))
        
        try:
            with transaction.atomic():
                # Clear existing data if requested
                if clear_data:
                    self.stdout.write('🗑️  Clearing existing data...')
                    User.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS('✅ Data cleared'))
                
                # Check if data already exists
                if User.objects.exists() and not clear_data:
                    self.stdout.write(
                        self.style.WARNING(
                            '⚠️  Database already contains data. Use --clear to reset.'
                        )
                    )
                    return
                
                # Create admin user
                self.stdout.write('👤 Creating admin user...')
                admin = AdminUserFactory(
                    username='admin',
                    email='admin@example.com'
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Admin user created: {admin.username} (password: password123)'
                    )
                )
                
                # Create staff user
                self.stdout.write('👤 Creating staff user...')
                staff = StaffUserFactory(
                    username='staff',
                    email='staff@example.com'
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Staff user created: {staff.username} (password: password123)'
                    )
                )
                
                # Create regular users
                self.stdout.write(f'👥 Creating {num_users} regular users...')
                users = UserFactory.create_batch(num_users)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Created {len(users)} regular users (user0-user{num_users-1})'
                    )
                )
                
                # Summary
                total_users = User.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🎉 Database seeding complete! Total users: {total_users}'
                    )
                )
                self.stdout.write('\n📝 Sample credentials:')
                self.stdout.write('   Admin: admin / password123')
                self.stdout.write('   Staff: staff / password123')
                self.stdout.write('   Users: user0-user9 / password123')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error seeding database: {e}')
            )
            logger.error(f'Database seeding failed: {e}', exc_info=True)
            raise
