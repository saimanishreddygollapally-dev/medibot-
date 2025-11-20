# Environment Variables Setup

Create a `.env` file in the root directory of the project with the following variables:

```env
# Flask Secret Key (change this to a random secret key in production)
SECRET_KEY=your-secret-key-here-change-in-production

# Database URL (SQLite by default, can be changed to PostgreSQL, MySQL, etc.)
DATABASE_URL=sqlite:///medibot.db

# Google OAuth 2.0 Credentials
# Get these from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Pinecone API Key (existing)
PINECONE_API_KEY=your-pinecone-api-key

# OpenRouter API Key (existing - if needed)
# OPENAI_API_KEY=your-openrouter-api-key
```

## Setting up Google OAuth 2.0

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
5. Copy the Client ID and Client Secret to your `.env` file

## OAuth Redirect URI

Make sure to add the callback URL to your Google OAuth consent screen:
- Local development: `http://localhost:8080/callback`
- Production: `https://yourdomain.com/callback`

## Generating a Secret Key

For production, generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

Use the output as your `SECRET_KEY` in the `.env` file.

