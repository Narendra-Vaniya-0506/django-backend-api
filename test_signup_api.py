import requests

url = "http://127.0.0.1:8000/api/signup/"
data = {
    "phone_number": "1234567890",
    "email": "test@example.com",
    "password": "TestPass123"
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
