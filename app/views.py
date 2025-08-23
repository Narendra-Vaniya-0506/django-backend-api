import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.permissions import AllowAny
from .serializers import UserProfileSerializer, UserProfileDetailSerializer
from .models import UserProfile, Contact
from django.core.mail import send_mail

logger = logging.getLogger(__name__)



def home(request):
    """Home page view for the root URL with modern styling."""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Backend</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

            body {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Inter', sans-serif;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                text-align: center;
            }

            .container {
                background-color: #1e1e1e;
                padding: 40px 50px;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                border: 1px solid #2a2a2a;
                max-width: 600px;
            }

            h1 {
                color: #ffffff;
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            p {
                font-size: 1.1em;
                line-height: 1.6;
                margin-bottom: 30px;
            }

            .admin-button {
                display: inline-block;
                background-color: #007bff;
                color: #ffffff;
                padding: 12px 25px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }

            .admin-button:hover {
                background-color: #0056b3;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to the Code Yatra Backend</h1>
            <p>This is Youtube backend server for the Code Yatra.</p>
            <a href="/admin/" class="admin-button">Admin Interface</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

@api_view(['GET'])
@permission_classes([AllowAny]) # Explicitly public, overriding settings.py default
def get_tutorials(request):
    """
    Returns a list of dummy tutorial data using DRF's Response.
    """
    tutorials = [
        {'id': 1, 'title': 'HTML & CSS Basics', 'mentor': 'Narendra'},
        {'id': 2, 'title': 'JavaScript Fundamentals', 'mentor': 'Narendra'},
        {'id': 3, 'title': 'React Deep Dive', 'mentor': 'Narendra'},
    ]
    return Response({
        'success': True,
        'data': tutorials
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def signup(request):
    """
    Register a new user using the UserProfileSerializer for validation.
    """
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        # .save() will call the create() method in our serializer
        user = serializer.save()
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user profile
        profile = user.profile
        
        return Response({
            'success': True,
            'data': {
                'token': token.key,
                'user': {
                    'email': user.email,
                    'phone_number': user.username,
                    'name': profile.name,
                    'lessons_started': profile.lessons_started,
                    'lessons_completed': profile.lessons_completed,
                    'join_date': profile.join_date
                }
            }
        }, status=status.HTTP_201_CREATED)
    
    # If validation fails, the serializer.errors dictionary will be returned
    # with detailed error messages for the frontend.
    return Response({
        'success': False,
        'error': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login(request):
    identifier = request.data.get('identifier')  # email or phone number
    password = request.data.get('password')

    if not identifier or not password:
        return Response({
            'success': False,
            'error': 'Missing identifier or password'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Determine username from identifier (email or phone number)
    username = None
    if '@' in identifier:
        try:
            # Find the user by email and get their username
            user_obj = User.objects.filter(email__iexact=identifier).first()
            if user_obj:
                username = user_obj.username
        except User.DoesNotExist:
            # To prevent user enumeration, we'll fail at the authentication step
            pass
    else:
        # Assume the identifier is the phone number (which is the username)
        username = identifier

    # Authenticate the user
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # User is valid, so create or retrieve their token
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user profile
        try:
            profile = user.profile
        except Exception:
            return Response({
                'success': False,
                'error': 'User profile does not exist.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'data': {
                'token': token.key,
                'user': {
                    'email': user.email,
                    'phone_number': user.username,
                    'name': profile.name,
                    'lessons_started': profile.lessons_started,
                    'lessons_completed': profile.lessons_completed,
                    'join_date': profile.join_date
                }
            }
        }, status=status.HTTP_200_OK)
    else:
        # Invalid credentials
        return Response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # This automatically protects the endpoint
def profile(request):
    """
    View to get the profile of the currently authenticated user.
    Return the data for the user attached to the validated token.
    """
    # `request.user` is populated by the authentication system after validating the token
    try:
        profile = request.user.profile
        serializer = UserProfileDetailSerializer(profile)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"Profile view error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not retrieve profile.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile (name, email)
    """
    try:
        profile = request.user.profile
        data = request.data
        
        # Update name
        if 'name' in data:
            profile.name = data['name']
        
        # Update email
        if 'email' in data:
            request.user.email = data['email']
            request.user.save()
        
        profile.save()
        
        serializer = UserProfileDetailSerializer(profile)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"Update profile error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not update profile.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_lesson(request):
    """
    Add lesson to lessons_started array
    """
    try:
        profile = request.user.profile
        lesson_id = request.data.get('lesson_id')
        
        if not lesson_id:
            return Response({
                'success': False,
                'error': 'lesson_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if lesson_id not in profile.lessons_started:
            profile.lessons_started.append(lesson_id)
            profile.save()
        
        serializer = UserProfileDetailSerializer(profile)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"Start lesson error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not start lesson.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_lesson(request):
    """
    Add lesson to lessons_completed array
    """
    try:
        profile = request.user.profile
        lesson_id = request.data.get('lesson_id')
        
        if not lesson_id:
            return Response({
                'success': False,
                'error': 'lesson_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if lesson_id not in profile.lessons_completed:
            profile.lessons_completed.append(lesson_id)
            # Remove from lessons_started if it exists
            if lesson_id in profile.lessons_started:
                profile.lessons_started.remove(lesson_id)
            profile.save()
        
        serializer = UserProfileDetailSerializer(profile)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"Complete lesson error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not complete lesson.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def contact(request):
    """
    Handle contact form submissions and send emails
    """
    try:
        data = request.data
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        subject = data.get('subject')
        message = data.get('message')

        # Validate required fields
        if not all([name, email, subject, message]):
            return Response({
                'success': False,
                'error': 'Name, email, subject, and message are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save contact to database
        contact = Contact.objects.create(
            name=name,
            email=email,
            phone=phone or '',
            subject=subject,
            message=message
        )

        # Send email to admin
        admin_subject = f"New Contact Form Submission: {subject}"
        admin_message = f"""
        New contact form submission received:

        Name: {name}
        Email: {email}
        Phone: {phone or 'Not provided'}
        Subject: {subject}
        Message: {message}

        Received at: {contact.created_at}
        """

        send_mail(
            admin_subject,
            admin_message,
            'codeyatra0605@gmail.com',
            ['codeyatra0605@gmail.com'],
            fail_silently=False,
        )

        # Send confirmation email to user
        user_subject = "Thank you for contacting Code Yatra"
        user_message = f"""
        Dear {name},

        Thank you for reaching out to us! We have received your message and will get back to you shortly.

        Here's a summary of your message:
        Subject: {subject}
        Message: {message}

        We appreciate your interest in Code Yatra.

        Best regards,
        Code Yatra Team
        """

        send_mail(
            user_subject,
            user_message,
            'codeyatra0605@gmail.com',
            [email],
            fail_silently=False,
        )

        return Response({
            'success': True,
            'message': 'Contact form submitted successfully. Emails sent.'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Contact form error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not process contact form submission.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
