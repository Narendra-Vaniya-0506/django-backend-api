from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Contact

from .models import Contact

admin.site.register(Contact)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Learning Progress', {
            'fields': ('lessons_started', 'lessons_completed'),
            'classes': ('collapse',)
        }),
        ('Account Info', {
            'fields': ('join_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('join_date',)

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'date_joined',
        'lessons_started_count',
        'lessons_completed_count',
        'profile_name'
    )
    
    list_filter = BaseUserAdmin.list_filter + ('profile__join_date',)
    
    search_fields = BaseUserAdmin.search_fields + ('profile__name',)
    
    def lessons_started_count(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile.lessons_started:
                return len(obj.profile.lessons_started)
            return 0
        except (AttributeError, TypeError):
            return 0
    
    lessons_started_count.short_description = 'Lessons Started'
    
    def lessons_completed_count(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile.lessons_completed:
                return len(obj.profile.lessons_completed)
            return 0
        except (AttributeError, TypeError):
            return 0
    
    lessons_completed_count.short_description = 'Lessons Completed'
    
    def profile_name(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile.name:
                return obj.profile.name
            return '-'
        except AttributeError:
            return '-'
    
    profile_name.short_description = 'Profile Name'

# Register UserProfile separately for direct access
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'join_date', 'lessons_started_count', 'lessons_completed_count')
    list_filter = ('join_date',)
    search_fields = ('user__username', 'user__email', 'name')
    readonly_fields = ('join_date',)
    
    def lessons_started_count(self, obj):
        try:
            return len(obj.lessons_started) if obj.lessons_started else 0
        except (TypeError, AttributeError):
            return 0
    
    lessons_started_count.short_description = 'Lessons Started'
    
    def lessons_completed_count(self, obj):
        try:
            return len(obj.lessons_completed) if obj.lessons_completed else 0
        except (TypeError, AttributeError):
            return 0
    
    lessons_completed_count.short_description = 'Lessons Completed'
