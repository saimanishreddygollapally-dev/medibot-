# MediBot Chat UI Update

## 🎉 New Features

### 1. Modern ChatGPT-like Interface
- Beautiful, professional UI built with TailwindCSS
- Left sidebar with user profile (Google photo, name) and chat history
- Main chat window with rounded message bubbles
- Smooth animations and transitions
- Auto-scroll to latest message

### 2. Chat History & Sessions
- Each user's chats are stored separately (linked to Google login)
- Sidebar lists previous chat sessions with timestamps
- Click on any chat to load its history
- Delete chat sessions with a click
- Create new chat sessions to start fresh conversations

### 3. Conversation Memory
- Uses LangChain ConversationBufferMemory to maintain context
- Bot remembers past context during a session
- When continuing a chat, memory is preloaded with previous conversation context
- Memory is cleared when starting a new chat

### 4. Dark/Light Mode
- Toggle between light and dark themes
- Preference is saved in localStorage
- Smooth transitions between themes

### 5. Mobile Responsive
- Fully responsive design
- Mobile sidebar with slide-in animation
- Touch-friendly interface
- Optimized for all screen sizes

## 📁 Database Changes

### New Tables
- **ChatSession**: Stores chat sessions with titles and timestamps
- **Chat**: Stores individual messages with user questions and bot responses

### Migration
The database will be automatically updated when you run the app. The new tables will be created automatically.

## 🚀 How to Use

### Starting a New Chat
1. Click the "New Chat" button in the sidebar
2. Start typing your message
3. Press Enter or click the Send button

### Viewing Chat History
1. All your previous chats are listed in the left sidebar
2. Click on any chat to load its history
3. Continue the conversation from where you left off

### Deleting a Chat
1. Hover over a chat in the sidebar
2. Click the trash icon that appears
3. Confirm deletion

### Toggling Dark Mode
1. Click the "Dark Mode" / "Light Mode" button in the sidebar
2. Your preference will be saved automatically

## 🔧 Technical Details

### Backend Routes
- `POST /api/chat` - Send a message and get a response
- `POST /api/chat/session/new` - Create a new chat session
- `GET /api/chat/session/<id>` - Get chat history for a session
- `POST /api/chat/session/<id>/load` - Load a session and initialize memory
- `DELETE /api/chat/session/<id>/delete` - Delete a chat session
- `GET /api/chat/sessions` - Get all chat sessions for the user

### Memory Management
- Memory buffers are stored in-memory per session (key: `{user_id}_{session_id}`)
- For production, consider using Redis or a similar solution for persistent memory storage
- Memory is loaded from the database when a session is opened
- Last 5 conversation exchanges are included in context to avoid token limits

## 📝 Notes

1. **Database**: The app will automatically create the new tables when you start it
2. **Memory**: Memory is stored in-memory, so it will be lost on server restart. For production, consider using Redis
3. **Session Management**: Each chat session maintains its own memory buffer
4. **Backward Compatibility**: The old `/get` endpoint still works for backward compatibility

## 🎨 UI Features

- Modern, clean design inspired by ChatGPT
- Rounded message bubbles
- Loading animations
- Smooth scroll behavior
- Custom scrollbars
- Responsive layout
- Dark mode support
- Font Awesome icons
- TailwindCSS for styling

## 🔐 Security

- All routes are protected with `@login_required`
- Users can only access their own chat sessions
- Database queries are filtered by user_id
- Session validation on all endpoints

Enjoy your new MediBot interface! 🚀

