from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=True, default='')
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
    
    def is_valid(self):
        # OTP expires after 10 minutes
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=10)
    
    @classmethod
    def generate_otp(cls, user):
        # Generate a 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        # Invalidate any existing OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        # Create new OTP
        return cls.objects.create(user=user, otp_code=otp_code)
    
    @classmethod
    def verify_otp(cls, user, otp_code):
        try:
            otp = cls.objects.get(user=user, otp_code=otp_code, is_used=False)
            if otp.is_valid():
                otp.is_used = True
                otp.save()
                return True
            return False
        except cls.DoesNotExist:
            return False
