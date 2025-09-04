# TODO: Remove Lesson Sessions Feature

## Information Gathered
- LessonSession model defined in app/models.py
- Registered in Django admin in app/admin.py
- Lesson-related methods (lessons_started_count, lessons_completed_count) in CustomUserAdmin
- Views in app/views.py: lesson_session_data, start_lesson, complete_lesson (already disabled)
- Serializers in app/serializers.py may have lesson-related fields
- Frontend may have lesson session related code

## Plan
1. Remove LessonSession model from app/models.py
2. Remove admin registration and lesson methods from app/admin.py
3. Remove or disable lesson-related views in app/views.py
4. Remove lesson-related fields from serializers in app/serializers.py
5. Check and remove frontend code related to lesson sessions
6. Create migration to remove the model

## Dependent Files to be edited
- app/models.py
- app/admin.py
- app/views.py
- app/serializers.py
- Frontend files (if any)

## Followup steps
- Create Django migration for model removal
- Test the application to ensure no errors
