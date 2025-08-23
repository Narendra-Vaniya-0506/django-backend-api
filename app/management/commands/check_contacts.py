from django.core.management.base import BaseCommand
from app.models import Contact

class Command(BaseCommand):
    help = 'Check contact entries in the database'

    def handle(self, *args, **options):
        contacts = Contact.objects.all()
        
        if contacts.exists():
            self.stdout.write(self.style.SUCCESS(f'Found {contacts.count()} contact entries:'))
            for contact in contacts:
                self.stdout.write(f'ID: {contact.id}, Name: {contact.name}, Email: {contact.email}, Subject: {contact.subject}, Created: {contact.created_at}')
        else:
            self.stdout.write(self.style.WARNING('No contact entries found in the database.'))
