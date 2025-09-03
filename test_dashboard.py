#!/usr/bin/env python
"""
Test script for the dashboard endpoint
"""
import requests
import json

# Replace with your actual API URL
API_BASE_URL = 'http://127.0.0.1:8000/api'

def test_dashboard_endpoint():
    """
    Test the dashboard endpoint with authentication
    """
    print("Testing Dashboard Endpoint")
    print("=" * 50)

    # First, we need to login to get a token
    login_data = {
        'identifier': 'test@example.com',  # Replace with actual test user
        'password': 'testpassword'  # Replace with actual password
    }

    print("1. Attempting login...")
    try:
        login_response = requests.post(f'{API_BASE_URL}/login/', json=login_data)
        print(f"Login response status: {login_response.status_code}")

        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get('success'):
                token = login_result['data']['token']
                print("✓ Login successful, got token")

                # Now test the dashboard endpoint
                print("\n2. Testing dashboard endpoint...")
                headers = {
                    'Authorization': f'Token {token}',
                    'Content-Type': 'application/json'
                }

                dashboard_response = requests.get(f'{API_BASE_URL}/dashboard/', headers=headers)
                print(f"Dashboard response status: {dashboard_response.status_code}")

                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    if dashboard_data.get('success'):
                        print("✓ Dashboard endpoint working correctly")
                        print("Dashboard data structure:")
                        data = dashboard_data['data']
                        print(f"  - User: {data['user']['name']}")
                        print(f"  - Courses Completed: {data['progressSummary']['coursesCompleted']}")
                        print(f"  - Total Courses: {data['progressSummary']['totalCourses']}")
                        print(f"  - Lessons Watched: {data['progressSummary']['lessonsWatched']}")
                        print(f"  - Experience Points: {data['progressSummary']['experiencePoints']}")
                        print(f"  - Enrolled Courses: {len(data['enrolledCourses'])}")
                    else:
                        print("✗ Dashboard returned success=False")
                        print(f"Error: {dashboard_data.get('error')}")
                else:
                    print(f"✗ Dashboard endpoint failed with status {dashboard_response.status_code}")
                    print(f"Response: {dashboard_response.text}")

            else:
                print("✗ Login failed")
                print(f"Error: {login_result.get('error')}")
        else:
            print(f"✗ Login request failed with status {login_response.status_code}")
            print(f"Response: {login_response.text}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")

    # Test without authentication
    print("\n3. Testing dashboard without authentication...")
    try:
        dashboard_response = requests.get(f'{API_BASE_URL}/dashboard/')
        print(f"Unauthenticated response status: {dashboard_response.status_code}")
        if dashboard_response.status_code == 401:
            print("✓ Correctly returns 401 for unauthenticated request")
        else:
            print(f"✗ Expected 401, got {dashboard_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")

if __name__ == '__main__':
    test_dashboard_endpoint()
