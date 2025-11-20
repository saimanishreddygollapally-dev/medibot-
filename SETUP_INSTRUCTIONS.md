# Setup Instructions for MediBot Chat UI Update

## ✅ Quick Answer: What Do You Need to Do?

**You can run directly!** The app will automatically:
- Create the new database tables when you start it
- Use existing dependencies (no new packages needed)

However, if you're setting up from scratch or want to ensure everything is installed:

## 📋 Step-by-Step Setup

### 1. Install/Update Dependencies (If Needed)

All required packages are already in `requirements.txt`. Just run:

```bash
pip install -r requirements.txt
```

**Note:** The `ConversationBufferMemory` is part of the `langchain` package which is already in your requirements, so no additional installation is needed.

### 2. Database Setup

**No manual migration needed!** The database tables will be created automatically when you run the app.

The app includes this code that runs on startup:
```python
with app.app_context():
    db.create_all()
```

This will automatically create:
- `users` table (if not exists)
- `chat_sessions` table (NEW)
- `chats` table (NEW)

### 3. Environment Variables

Make sure your `.env` file has these variables (you should already have them):

```env
# Flask Secret Key
SECRET_KEY=your-secret-key-here-change-in-production

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///medibot.db

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Pinecone API Key
PINECONE_API_KEY=your-pinecone-api-key
```

### 4. Run the Application

Simply run:

```bash
python app.py
```

The app will:
1. ✅ Automatically create new database tables
2. ✅ Start on `http://localhost:5000` (or the port specified in app.py)
3. ✅ Be ready to use with the new chat UI

## 🚀 First Run Checklist

When you run the app for the first time:

1. ✅ Database tables are created automatically
2. ✅ Login with Google (if not already logged in)
3. ✅ Start chatting - your conversations will be saved
4. ✅ View chat history in the sidebar
5. ✅ Toggle dark/light mode

## 🔍 Verification

To verify everything is working:

1. **Check Database**: Look for `instance/medibot.db` file (or your database file)
2. **Check Tables**: The database should have 3 tables:
   - `users`
   - `chat_sessions` (NEW)
   - `chats` (NEW)
3. **Test Chat**: Send a message and check if it appears in the sidebar
4. **Test History**: Create a new chat, send messages, then check if they're saved

## ⚠️ Troubleshooting

### Issue: Import Error for ConversationBufferMemory

**Solution:** Update langchain packages:
```bash
pip install --upgrade langchain langchain-community
```

### Issue: Database Tables Not Created

**Solution:** The tables are created on first run. If they're not created:
1. Delete the existing database file (`instance/medibot.db`)
2. Restart the app - it will create fresh tables

### Issue: Chat History Not Showing

**Solution:** 
1. Make sure you're logged in
2. Send at least one message in a chat
3. Refresh the page
4. Check browser console for errors

### Issue: Memory Not Working

**Solution:** Memory is stored in-memory (will be lost on server restart). This is normal for development. For production, consider using Redis.

## 📝 What Changed?

- ✅ New database models (`ChatSession`, `Chat`)
- ✅ New API endpoints for chat history
- ✅ New UI with TailwindCSS
- ✅ Memory management with LangChain
- ✅ Dark/Light mode toggle
- ✅ Mobile responsive design

## 🎯 Summary

**You can run directly!** Just:
1. Make sure dependencies are installed: `pip install -r requirements.txt`
2. Run the app: `python app.py`
3. Database tables will be created automatically
4. Start using the new features!

No manual database migration or additional setup required! 🚀

