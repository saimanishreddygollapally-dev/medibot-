from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from src.prompt import *
from src.models import db, User, ChatSession, Chat
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import os
import requests
import uuid

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Flask configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///medibot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the chatbot.'

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()

# Load embeddings and set up RAG chain
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

embeddings = download_hugging_face_embeddings()

index_name = "medical-chatbot"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

chatModel = ChatOpenAI(
    model_name="mistralai/mistral-small-3.2-24b-instruct:free",
    openai_api_base="https://openrouter.ai/api/v1",
    #openai_api_key="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"
    openai_api_key="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"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Store memory buffers per session (in production, use Redis or similar)
session_memories = {}


# Routes
@app.route("/")
def index():
    """Redirect to chat if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('chat_page'))
    return redirect(url_for('login'))


@app.route("/login")
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('chat_page'))
    return render_template('login.html')


@app.route("/login/google")
def google_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = google.authorize_access_token()
        
        # Fetch user info from Google API
        # Try using Authlib's get method first
        try:
            user_info = google.get('userinfo', token=token).json()
        except:
            # Fallback: fetch directly from Google's userinfo endpoint
            access_token = token.get('access_token')
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_info = user_info_response.json()
        
        # Extract user information
        google_id = user_info.get('sub') or user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name')
        profile_pic = user_info.get('picture')
        
        if not google_id or not email:
            raise ValueError("Missing required user information from Google")
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                profile_pic=profile_pic
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update user info if needed
            user.email = email
            user.name = name
            if profile_pic:
                user.profile_pic = profile_pic
            user.last_login = datetime.utcnow()
            db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)
        
        return redirect(url_for('chat_page'))
    
    except Exception as e:
        print(f"Error during OAuth callback: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('login'))


@app.route("/logout")
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('login'))


@app.route("/chat")
@login_required
def chat_page():
    """Chatbot interface page (protected)"""
    # Get user's chat sessions
    chat_sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).all()
    sessions_data = [session.to_dict() for session in chat_sessions] if chat_sessions else []
    return render_template('chat.html', user=current_user, chat_sessions=sessions_data)


@app.route("/api/chat/session/new", methods=["POST"])
@login_required
def new_chat_session():
    """Create a new chat session"""
    try:
        session = ChatSession(user_id=current_user.id)
        db.session.add(session)
        db.session.commit()
        
        # Initialize memory for this session
        session_key = f"{current_user.id}_{session.id}"
        session_memories[session_key] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        return jsonify({"success": True, "session_id": session.id}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat/session/<int:session_id>", methods=["GET"])
@login_required
def get_chat_session(session_id):
    """Get chat history for a specific session"""
    try:
        session_obj = ChatSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first_or_404()
        
        chats = [chat.to_dict() for chat in session_obj.chats]
        return jsonify({
            "success": True,
            "session": session_obj.to_dict(),
            "chats": chats
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat/sessions", methods=["GET"])
@login_required
def get_chat_sessions():
    """Get all chat sessions for the current user"""
    try:
        sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(
            ChatSession.updated_at.desc()
        ).all()
        sessions_data = [session.to_dict() for session in sessions]
        return jsonify({"success": True, "sessions": sessions_data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat/session/<int:session_id>/load", methods=["POST"])
@login_required
def load_chat_session(session_id):
    """Load a chat session and initialize memory with history"""
    try:
        session_obj = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first_or_404()
        
        # Initialize or clear memory for this session
        session_key = f"{current_user.id}_{session_id}"
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Load previous conversations into memory
        for chat in session_obj.chats:
            memory.chat_memory.add_user_message(chat.message)
            memory.chat_memory.add_ai_message(chat.response)
        
        session_memories[session_key] = memory
        
        chats = [chat.to_dict() for chat in session_obj.chats]
        return jsonify({
            "success": True,
            "session": session_obj.to_dict(),
            "chats": chats
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat/session/<int:session_id>/delete", methods=["DELETE"])
@login_required
def delete_chat_session(session_id):
    """Delete a chat session"""
    try:
        session_obj = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first_or_404()
        
        # Clear memory
        session_key = f"{current_user.id}_{session_id}"
        if session_key in session_memories:
            del session_memories[session_key]
        
        db.session.delete(session_obj)
        db.session.commit()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    """Chat API endpoint with memory and database storage"""
    try:
        data = request.get_json()
        msg = data.get("msg", "").strip()
        session_id = data.get("session_id")
        
        if not msg:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
        # Get or create session
        if session_id:
            session_obj = ChatSession.query.filter_by(
                id=session_id,
                user_id=current_user.id
            ).first()
            if not session_obj:
                return jsonify({"success": False, "error": "Session not found"}), 404
        else:
            # Create new session
            session_obj = ChatSession(user_id=current_user.id, title=msg[:100])
            db.session.add(session_obj)
            db.session.commit()
            session_id = session_obj.id
        
        # Get or initialize memory for this session
        session_key = f"{current_user.id}_{session_id}"
        if session_key not in session_memories:
            memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
            # Load existing history if any
            for chat in session_obj.chats:
                memory.chat_memory.add_user_message(chat.message)
                memory.chat_memory.add_ai_message(chat.response)
            session_memories[session_key] = memory
        else:
            memory = session_memories[session_key]
        
        # Update session title if this is the first message
        if not session_obj.title and len(session_obj.chats) == 0:
            session_obj.title = msg[:100]
        
        # Build conversation context from memory
        # Get the last few exchanges for context (last 5 exchanges = 10 messages)
        history_messages = memory.chat_memory.messages
        conversation_context = ""
        
        if history_messages:
            # Take last 10 messages (5 exchanges) for context to avoid token limits
            recent_messages = history_messages[-10:] if len(history_messages) > 10 else history_messages
            
            for i in range(0, len(recent_messages), 2):
                if i < len(recent_messages):
                    user_content = recent_messages[i].content if hasattr(recent_messages[i], 'content') else str(recent_messages[i])
                    conversation_context += f"Previous User Question: {user_content}\n"
                if i + 1 < len(recent_messages):
                    ai_content = recent_messages[i+1].content if hasattr(recent_messages[i+1], 'content') else str(recent_messages[i+1])
                    conversation_context += f"Previous Assistant Answer: {ai_content}\n"
        
        # Prepare input with conversation context
        if conversation_context:
            # Include context in the input to help the model understand the conversation flow
            enhanced_input = f"Conversation History:\n{conversation_context}\n\nCurrent User Question: {msg}\n\nPlease provide a helpful answer considering the conversation history above."
        else:
            enhanced_input = msg
        
        # Invoke RAG chain
        response = rag_chain.invoke({"input": enhanced_input})
        answer = str(response["answer"])
        
        # Store in memory for future context
        memory.chat_memory.add_user_message(msg)
        memory.chat_memory.add_ai_message(answer)
        
        # Save to database
        chat = Chat(
            session_id=session_id,
            user_id=current_user.id,
            message=msg,
            response=answer
        )
        db.session.add(chat)
        session_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "response": answer,
            "session_id": session_id
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# Legacy endpoint for backward compatibility
@app.route("/get", methods=["GET", "POST"])
@login_required
def chat_legacy():
    """Legacy chat API endpoint (protected)"""
    msg = request.form.get("msg", "")
    if not msg:
        return "Message cannot be empty", 400
    
    # Create a temporary session for legacy requests
    session_obj = ChatSession(user_id=current_user.id, title=msg[:100])
    db.session.add(session_obj)
    db.session.commit()
    
    session_key = f"{current_user.id}_{session_obj.id}"
    session_memories[session_key] = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history"
    )
    
    response = rag_chain.invoke({"input": msg})
    answer = str(response["answer"])
    
    # Store in memory and database
    session_memories[session_key].chat_memory.add_user_message(msg)
    session_memories[session_key].chat_memory.add_ai_message(answer)
    
    chat = Chat(
        session_id=session_obj.id,
        user_id=current_user.id,
        message=msg,
        response=answer
    )
    db.session.add(chat)
    db.session.commit()
    
    return answer


#if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
