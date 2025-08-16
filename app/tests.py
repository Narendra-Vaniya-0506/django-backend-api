import json
from django.test import TestCase, Client
from django.urls import reverse

class UserApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        url = reverse('signup')
        data = {
            "email": "test@example.com",
            "phone_number": "1234567890",
            "password": "testpass123",
            "name": "Test User"
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json().get('success'))
        self.assertIn('token', response.json()['data'])

    def test_login(self):
        # First signup
        self.test_signup()
        url = reverse('login')
        data = {
            "identifier": "test@example.com",
            "password": "testpass123"
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertIn('token', response.json()['data'])

    def test_profile_update(self):
        self.test_signup()
        login_url = reverse('login')
        login_data = {
            "identifier": "test@example.com",
            "password": "testpass123"
        }
        login_response = self.client.post(login_url, data=json.dumps(login_data), content_type='application/json')
        token = login_response.json()['data']['token']

        url = reverse('update_profile')
        update_data = {
            "name": "Updated User",
            "email": "updated@example.com"
        }
        response = self.client.patch(url, data=json.dumps(update_data), content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(response.json()['data']['name'], "Updated User")
        self.assertEqual(response.json()['data']['email'], "updated@example.com")

    def test_start_and_complete_lesson(self):
        self.test_signup()
        login_url = reverse('login')
        login_data = {
            "identifier": "test@example.com",
            "password": "testpass123"
        }
        login_response = self.client.post(login_url, data=json.dumps(login_data), content_type='application/json')
        token = login_response.json()['data']['token']

        start_url = reverse('start_lesson')
        complete_url = reverse('complete_lesson')

        lesson_id = "lesson1"

        # Start lesson
        start_response = self.client.post(start_url, data=json.dumps({"lesson_id": lesson_id}), content_type='application/json',
                                          HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(start_response.status_code, 200)
        self.assertTrue(start_response.json().get('success'))
        self.assertIn(lesson_id, start_response.json()['data']['lessons_started'])

        # Complete lesson
        complete_response = self.client.post(complete_url, data=json.dumps({"lesson_id": lesson_id}), content_type='application/json',
                                             HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(complete_response.status_code, 200)
        self.assertTrue(complete_response.json().get('success'))
        self.assertIn(lesson_id, complete_response.json()['data']['lessons_completed'])
        self.assertNotIn(lesson_id, complete_response.json()['data']['lessons_started'])
