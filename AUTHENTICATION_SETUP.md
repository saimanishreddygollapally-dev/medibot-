# Google OAuth Authentication Setup

MediBot now includes Google Sign-In authentication. This document explains how to set up and use the authentication system.

## Features

- ✅ Google OAuth 2.0 authentication
- ✅ User session management with Flask-Login
- ✅ User database with SQLAlchemy
- ✅ Protected routes (chat requires login)
- ✅ User profile display (name, email, profile picture)
- ✅ Secure logout functionality

## Setup Instructions

### 1. Install Dependencies

Make sure you have installed all the required packages:

```bash
pip install -r requirements.txt
```

The new dependencies include:
- `flask-login` - For session management
- `flask-sqlalchemy` - For database operations
- `authlib` - For OAuth 2.0 integration
- `requests` - For HTTP requests

### 2. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - For local development: `http://localhost:8080/callback`
     - For production: `https://yourdomain.com/callback`
5. Copy the Client ID and Client Secret

### 3. Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Secret Key (generate a random secret key for production)
SECRET_KEY=your-secret-key-here-change-in-production

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///medibot.db

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Existing API keys
PINECONE_API_KEY=your-pinecone-api-key
```

### 4. Generate Secret Key

For production, generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

### 5. Initialize Database

The database will be automatically created when you run the app for the first time. The User table will be created with the following fields:
- `id` - Primary key
- `google_id` - Unique Google user ID
- `name` - User's display name
- `email` - User's email address
- `profile_pic` - User's profile picture URL (optional)
- `created_at` - Account creation timestamp
- `last_login` - Last login timestamp

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:8080`.

## Usage

### User Flow

1. **Unauthenticated users** visiting `/` or `/chat` will be redirected to `/login`
2. **Login page** displays a "Sign in with Google" button
3. **After clicking**, users are redirected to Google's authentication page
4. **After authentication**, users are redirected back to `/chat`
5. **Chat interface** displays user's name and profile picture (if available)
6. **Logout button** in the chat header allows users to sign out

### Routes

- `/` - Redirects to `/chat` if authenticated, otherwise to `/login`
- `/login` - Login page with Google Sign-In button
- `/login/google` - Initiates Google OAuth flow
- `/callback` - Google OAuth callback handler
- `/chat` - Chatbot interface (protected, requires login)
- `/get` - Chat API endpoint (protected, requires login)
- `/logout` - Logout route (protected, requires login)

### Database

The application uses SQLite by default (can be changed to PostgreSQL, MySQL, etc. by modifying `DATABASE_URL`).

Database file: `medibot.db` (created automatically)

## Security Notes

1. **Secret Key**: Always use a strong, randomly generated secret key in production
2. **Database**: For production, consider using PostgreSQL or MySQL instead of SQLite
3. **HTTPS**: Always use HTTPS in production for secure OAuth callbacks
4. **Environment Variables**: Never commit `.env` file to version control
5. **OAuth Credentials**: Keep your Google OAuth credentials secure

## Troubleshooting

### Common Issues

1. **"Redirect URI mismatch" error**
   - Make sure the redirect URI in Google Console matches exactly: `http://localhost:8080/callback`
   - For production, use: `https://yourdomain.com/callback`

2. **Database errors**
   - Make sure you have write permissions in the application directory
   - Check that `DATABASE_URL` is correctly set

3. **OAuth callback errors**
   - Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
   - Check that Google+ API is enabled in Google Cloud Console

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

## Production Deployment

When deploying to production:

1. Set `SECRET_KEY` to a strong random value
2. Use a production database (PostgreSQL recommended)
3. Update `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` if needed
4. Add production redirect URI to Google OAuth settings
5. Use HTTPS for all OAuth callbacks
6. Set `debug=False` in `app.py`

