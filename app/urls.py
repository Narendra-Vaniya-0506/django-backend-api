from django.urls import path
from . import views


urlpatterns = [
    path('tutorials/', views.get_tutorials, name='get_tutorials'),
    
    # Authentication endpoints
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    
    # Forgot password endpoints
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Profile endpoints
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Contact endpoint
    path('contact/', views.contact, name='contact'),

]
