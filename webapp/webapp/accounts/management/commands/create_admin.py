from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates the initial admin user with default credentials'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for admin account'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for admin account'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@verso-store.com',
            help='Email for admin account'
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Do not prompt for confirmation'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists.')
            )
            
            if not options['noinput']:
                confirm = input('Do you want to update the password? (yes/no): ')
                if confirm.lower() != 'yes':
                    return
            
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Password updated for admin user "{username}".')
            )
        else:
            # Create admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin',
                is_staff=True,
                is_superuser=True,
                first_name='Admin',
                last_name='User',
                email_verified=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Admin user "{username}" created successfully.')
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Default credentials:\n'
                    f'  Username: {username}\n'
                    f'  Password: {password}\n'
                    f'  Email: {email}\n'
                    f'IMPORTANT: Please change the password after first login!'
                )
            )