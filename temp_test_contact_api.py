import requests
import json

# Test the contact API endpoint
url = "http://localhost:8000/api/contact/"
data = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "subject": "Test Contact Form",
    "message": "This is a test message from the contact form."
}

try:
    response = requests.post(url, json=data, auth=('codeyatra0605@gmail.com', 'wmtx hdfw kwit clej'))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    print(f"Raw response: {response.text}")
