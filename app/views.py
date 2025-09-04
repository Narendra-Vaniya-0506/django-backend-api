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
from .models import UserProfile, Contact, PasswordResetOTP, Course, Lesson, UserCourseEnrollment, UserLessonProgress, ProjectSubmission
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
        
        # Send welcome email to the new user
        try:
            user_subject = "Welcome to Code Yatra!"
            user_message = f"""
            Dear {profile.name},

            Welcome to Code Yatra! We're excited to have you on board.

            Your account has been successfully created with the following details:
            Name: {profile.name}
            Email: {user.email}
            Phone Number: {user.username}
            
            You can now access our Free lessons and start your coding journey.

            If you have any questions or need assistance, feel free to contact us.

            Happy coding!

            Best regards,
            The Code Yatra Team
            """

            send_mail(
                user_subject,
                user_message,
                'codeyatra0605@gmail.com',
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Welcome email sent to: {user.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}", exc_info=True)
            # Continue with the signup process even if email fails
        
        return Response({
            'success': True,
            'data': {
                'token': token.key,
                'user': {
                    'email': user.email,
                    'phone_number': user.username,
                    'name': profile.name,
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

from django.utils import timezone
from .models import LessonSession

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_lesson(request):
    import traceback
    user = request.user
    try:
        lesson_id = request.data.get('lesson_id')
        logger.info(f"start_lesson called with lesson_id: {lesson_id} by user: {user}")
        if not lesson_id:
            logger.warning("start_lesson failed: lesson_id is missing")
            return Response({'success': False, 'error': 'lesson_id is required'}, status=400)
        try:
            # Try to get lesson by title field
            lesson = Lesson.objects.get(title=lesson_id)
        except Lesson.DoesNotExist:
            logger.warning(f"start_lesson failed: Lesson with title {lesson_id} not found")
            return Response({'success': False, 'error': 'Lesson not found'}, status=404)
        
        # Check if a session already started and not ended for this user and lesson
        existing_session = LessonSession.objects.filter(user=user, lesson=lesson, end_time__isnull=True).first()
        if existing_session:
            logger.warning(f"start_lesson failed: Lesson already started for user {user} and lesson {lesson_id}")
            return Response({'success': False, 'error': 'Lesson already started'}, status=400)
        
        # Create new lesson session with start_time now
        session = LessonSession.objects.create(user=user, lesson=lesson, start_time=timezone.now())
        logger.info(f"start_lesson success: Created session {session.id} for user {user} and lesson {lesson_id}")
        
        return Response({'success': True, 'message': 'Lesson started', 'session_id': session.id})
    except Exception as e:
        traceback_str = traceback.format_exc()
        logger.error(f"Exception in start_lesson: {e}\n{traceback_str}")
        return Response({'success': False, 'error': 'Internal server error'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_lesson(request):
    user = request.user
    lesson_id = request.data.get('lesson_id')
    if not lesson_id:
        return Response({'success': False, 'error': 'lesson_id is required'}, status=400)
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'success': False, 'error': 'Lesson not found'}, status=404)
    
    # Find the active session for this user and lesson
    session = LessonSession.objects.filter(user=user, lesson=lesson, end_time__isnull=True).first()
    if not session:
        return Response({'success': False, 'error': 'No active lesson session found'}, status=400)
    
    session.end_time = timezone.now()
    session.save()
    
    # Update UserLessonProgress to mark lesson completed
    lesson_progress, created = UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)
    lesson_progress.completed = True
    lesson_progress.save()

    # Update course progress
    course = lesson.course
    enrollment = UserCourseEnrollment.objects.filter(user=user, course=course).first()
    if enrollment:
        total_lessons = course.lessons.count()
        completed_lessons = UserLessonProgress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        ).count()
        if total_lessons > 0:
            enrollment.progress = (completed_lessons / total_lessons) * 100
            enrollment.save()

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

        logger.info(f"Received contact form data: {data}")
        contact = Contact.objects.create(
            name=name,
            email=email,
            phone=phone or '',
            subject=subject,
            message=message
        )

        logger.info(f"Contact entry saved: {contact.id}")
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

        # Validate email format
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            logger.error(f"Invalid email address: {email}")
            return Response({
                'success': False,
                'error': 'Invalid email address provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            logger.error(f"Invalid email address: {email}")
            return Response({
                'success': False,
                'error': 'Invalid email address provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send confirmation email to user
        logger.info(f"Sending confirmation email to: {email}")
        user_subject = "Thank you for contacting Code Yatra"
        user_message = f"""
        Dear {name},

        Thank you for reaching out to us! We have received,
        your message and will get back to you shortly.

        Here's a summary of your message:
        Subject : {subject}
        Message : {message}

        We appreciate your interest in Code Yatra.

        Best regards,
        The Code Yatra Team
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

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def forgot_password(request):
    """
    Generate and send OTP for password reset
    """
    try:
        identifier = request.data.get('identifier')
        
        if not identifier:
            return Response({
                'success': False,
                'error': 'Email or phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find user by email or phone number
        user = None
        if '@' in identifier:
            try:
                user = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                pass
        else:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                # Don't reveal if phone number exists for security
                pass

        if user:
            # Generate OTP
            otp = PasswordResetOTP.generate_otp(user)
            
            # Determine if we should send via email or SMS
            if '@' in identifier:
                # Send OTP via email
                try:
                    subject = "Password Reset OTP - Code Yatra"
                    message = f"""
                    Dear {user.profile.name},

                    You have requested to reset your password. 
                    Your One-Time Password (OTP) is: {otp.otp_code}

                    This OTP is valid for 10 minutes.

                    If you did not request this password reset, please ignore this email.

                    Best regards,
                    The Code Yatra Team
                    """

                    send_mail(
                        subject,
                        message,
                        'codeyatra0605@gmail.com',
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f"Password reset OTP sent to: {user.email}")

                except Exception as e:
                    logger.error(f"Failed to send OTP email to {user.email}: {e}", exc_info=True)
                    return Response({
                        'success': False,
                        'error': 'Failed to send OTP. Please try again later.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    # Phone number OTP sending removed - only email supported
                    logger.warning(f"Phone number OTP requested for {identifier}, but only email OTP is supported")
                    return Response({
                        'success': False,
                        'error': 'OTP can only be sent via email. Please use your email address.'
                    }, status=status.HTTP_400_BAD_REQUEST)

        # Always return success to prevent user enumeration
        return Response({
            'success': True,
            'message': 'If the email/phone number exists in our system, an OTP has been sent.'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Forgot password error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not process password reset request.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def reset_password(request):
    """
    Verify OTP and reset password
    """
    try:
        identifier = request.data.get('identifier')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        
        if not all([identifier, otp_code, new_password]):
            return Response({
                'success': False,
                'error': 'Email/phone, OTP code, and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find user by email or phone number
        user = None
        if '@' in identifier:
            try:
                user = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid credentials'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid credentials'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if not PasswordResetOTP.verify_otp(user, otp_code):
            return Response({
                'success': False,
                'error': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(new_password)
        user.save()

        logger.info(f"Password reset successfully for user: {user.username}")

        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Reset password error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not reset password.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    Get dashboard data for the authenticated user
    """
    try:
        user = request.user
        profile = user.profile

        # Get enrolled courses
        enrollments = UserCourseEnrollment.objects.filter(user=user).select_related('course')
        enrolled_courses = []

        total_courses = Course.objects.filter(is_active=True).count()
        courses_completed = 0
        lessons_watched = 0
        projects_submitted = 0

        for enrollment in enrollments:
            course = enrollment.course
            if enrollment.progress >= 100:
                courses_completed += 1

            # Get project submission status
            project_status = 'not-started'
            try:
                project = ProjectSubmission.objects.get(user=user, course=course)
                project_status = project.status
                if project.status == 'submitted':
                    projects_submitted += 1
            except ProjectSubmission.DoesNotExist:
                pass

            enrolled_courses.append({
                'id': course.id,
                'title': course.title,
                'progress': enrollment.progress,
                'projectStatus': project_status.replace('-', ' '),
                'isLocked': False  # For now, assume all enrolled courses are unlocked
            })

            # Count lessons watched for this course
            lessons_watched += UserLessonProgress.objects.filter(
                user=user,
                lesson__course=course,
                completed=True
            ).count()

        # Get continue learning data
        continue_learning = {
            'courseTitle': 'No courses in progress',
            'lessonTitle': '',
            'progress': 0
        }

        if enrollments.exists():
            # Find the course with highest progress but not completed
            in_progress = enrollments.filter(progress__lt=100).order_by('-progress').first()
            if in_progress:
                # Find the last watched lesson
                last_lesson = UserLessonProgress.objects.filter(
                    user=user,
                    lesson__course=in_progress.course
                ).order_by('-watched_at').first()

                if last_lesson:
                    continue_learning = {
                        'courseTitle': in_progress.course.title,
                        'lessonTitle': last_lesson.lesson.title,
                        'progress': in_progress.progress
                    }
                else:
                    # No lessons watched yet, get first lesson
                    first_lesson = in_progress.course.lessons.first()
                    if first_lesson:
                        continue_learning = {
                            'courseTitle': in_progress.course.title,
                            'lessonTitle': first_lesson.title,
                            'progress': in_progress.progress
                        }

        dashboard_data = {
            'user': {
                'name': profile.name or user.username
            },
            'progressSummary': {
                'coursesCompleted': courses_completed,
                'totalCourses': total_courses,
                'projectsSubmitted': projects_submitted,
                'lessonsWatched': lessons_watched,
                'experiencePoints': profile.experience_points
            },
            'continueLearning': continue_learning,
            'enrolledCourses': enrolled_courses
        }

        return Response({
            'success': True,
            'data': dashboard_data
        })

    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not retrieve dashboard data.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lesson_session_data(request):
    """
    Get progress summary and continue learning data for the lesson session page
    """
    try:
        user = request.user
        profile = user.profile

        # Get enrolled courses
        enrollments = UserCourseEnrollment.objects.filter(user=user).select_related('course')
        enrolled_courses = []

        total_courses = Course.objects.filter(is_active=True).count()
        courses_completed = 0
        lessons_watched = 0
        projects_submitted = 0

        for enrollment in enrollments:
            course = enrollment.course
            if enrollment.progress >= 100:
                courses_completed += 1

            # Get project submission status
            project_status = 'not-started'
            try:
                project = ProjectSubmission.objects.get(user=user, course=course)
                project_status = project.status
                if project.status == 'submitted':
                    projects_submitted += 1
            except ProjectSubmission.DoesNotExist:
                pass

            enrolled_courses.append({
                'id': course.id,
                'title': course.title,
                'progress': enrollment.progress,
                'projectStatus': project_status.replace('-', ' '),
                'isLocked': False  # For now, assume all enrolled courses are unlocked
            })

            # Count lessons watched for this course
            lessons_watched += UserLessonProgress.objects.filter(
                user=user,
                lesson__course=course,
                completed=True
            ).count()

        # Get continue learning data
        continue_learning = {
            'courseTitle': 'No courses in progress',
            'lessonTitle': '',
            'progress': 0
        }

        if enrollments.exists():
            # Find the course with highest progress but not completed
            in_progress = enrollments.filter(progress__lt=100).order_by('-progress').first()
            if in_progress:
                # Find the last watched lesson
                last_lesson = UserLessonProgress.objects.filter(
                    user=user,
                    lesson__course=in_progress.course
                ).order_by('-watched_at').first()

                if last_lesson:
                    continue_learning = {
                        'courseTitle': in_progress.course.title,
                        'lessonTitle': last_lesson.lesson.title,
                        'progress': in_progress.progress
                    }
                else:
                    # No lessons watched yet, get first lesson
                    first_lesson = in_progress.course.lessons.first()
                    if first_lesson:
                        continue_learning = {
                            'courseTitle': in_progress.course.title,
                            'lessonTitle': first_lesson.title,
                            'progress': in_progress.progress
                        }

        lesson_data = {
            'progressSummary': {
                'coursesCompleted': courses_completed,
                'totalCourses': total_courses,
                'projectsSubmitted': projects_submitted,
                'lessonsWatched': lessons_watched
            },
            'continueLearning': continue_learning
        }

        return Response({
            'success': True,
            'data': lesson_data
        })

    except Exception as e:
        logger.error(f"Lesson session data error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Could not retrieve lesson session data.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
