# Quiz Master Updates

## Database Schema Alignment

The code base has been updated to align with the existing database schema. The following changes were made:

1. Updated the User model:
   - Changed `username` to `full_name`
   - Changed `password_hash` to `password`
   - Added `date_of_birth`, `created_at`, `qualification` fields

2. Authentication fixes:
   - Updated registration form to include qualification field
   - Fixed login functionality to use correct password field name
   - Created a compatibility property to handle code expecting username

3. Admin account creation:
   - Improved error handling during admin account creation
   - Added global flag for tracking admin creation attempts
   - Added proper error handling with db session rollback

4. URL routing fixes:
   - Updated template references to use correct URL endpoints
   - Fixed navigation in base template

## Running the Application

The application can be run using:

```
./start_app.sh
```

This will start the Flask application on port 5000.

## Default Admin Credentials

The default admin credentials are:
- Email: admin@quizmaster.com
- Password: adminpass