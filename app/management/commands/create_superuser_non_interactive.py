import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    """
    Creates a superuser non-interactively, using environment variables.
    """
    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Creating account for {username} ({email})')
            User.objects.create_superuser(email=email, username=username, password=password)
        else:
            self.stdout.write('Superuser already exists. Skipping.')