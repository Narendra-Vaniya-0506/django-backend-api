import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class ContactFormTests(APITestCase):
    def test_contact_form_valid_email(self):
        """Test submitting the contact form with a valid email."""
        url = reverse('contact')  # Adjust the URL name as necessary
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)

    def test_contact_form_invalid_email(self):
        """Test submitting the contact form with an invalid email."""
        url = reverse('contact')  # Adjust the URL name as necessary
        data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('Invalid email address provided.', response.data['error'])

# Add more tests as needed
