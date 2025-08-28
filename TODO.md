# TODO: Remove "Learning Progress" Feature

## Database Model
- [x] Remove `lessons_started` and `lessons_completed` fields from `UserProfile` model in `app/models.py`

## API Endpoints
- [x] Remove `start_lesson` and `complete_lesson` view functions from `app/views.py`
- [x] Remove URL patterns for these endpoints from `app/urls.py`

## Admin Interface
- [x] Remove admin interface code for these fields from `app/admin.py`

## Database Migration
- [x] Create a new database migration to drop these fields from the database
