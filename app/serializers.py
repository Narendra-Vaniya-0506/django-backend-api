from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.core.validators import EmailValidator
import re
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    # Add explicit validators for clear error messages.
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )
    # The source='username' correctly maps this to the User model's username field.
    phone_number = serializers.CharField(
        source='username',
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this phone number already exists.")]
    )
    # write_only=True ensures the password is used for creation but not sent in responses.
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    name = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'name']

    def validate_email(self, value):
        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except Exception:
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_phone_number(self, value):
        # Validate mobile number format (10 digits, numeric only)
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be 10 digits and numeric.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        # Use create_user to ensure the password is properly hashed.
        user = User.objects.create_user(
            username=validated_data['username'], # Remember, phone_number is the username
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Create UserProfile
        UserProfile.objects.create(user=user, name=name)
        return user

class UserProfileDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField()
    lessons_started = serializers.JSONField()
    lessons_completed = serializers.JSONField()
    join_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'phone_number', 'name', 'lessons_started', 'lessons_completed', 'join_date']
