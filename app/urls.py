from django.urls import path
from . import views


urlpatterns = [
    path('tutorials/', views.get_tutorials, name='get_tutorials'),
    
    # Authentication endpoints
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),

    # Profile endpoints
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Lesson tracking endpoints
    path('lessons/start/', views.start_lesson, name='start_lesson'),
    path('lessons/complete/', views.complete_lesson, name='complete_lesson'),
]
