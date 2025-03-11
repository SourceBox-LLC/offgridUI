from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
import json

# Create database directory if it doesn't exist
os.makedirs('db', exist_ok=True)

# Create database engine
engine = create_engine('sqlite:///db/offgrid_chats.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class ChatSession(Base):
    """Represents a chat conversation session."""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default="New Chat")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship with messages
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }

class Message(Base):
    """Represents a single message in a chat."""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'))
    role = Column(String(20), nullable=False)  # 'system', 'user', or 'assistant'
    content = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with session
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self):
        """Convert message to dictionary for Streamlit."""
        result = {
            "id": self.id,
            "role": self.role,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.content:
            result["content"] = self.content
            
        if self.image_path:
            result["image"] = self.image_path
            
        return result

# Create all tables
Base.metadata.create_all(engine)

def create_new_chat_session(name="New Chat"):
    """Create a new chat session with a system message."""
    db_session = Session()
    
    try:
        # Create new chat session
        chat_session = ChatSession(name=name)
        db_session.add(chat_session)
        db_session.flush()  # To get the chat_session.id
        
        # Add system message
        system_message = Message(
            session_id=chat_session.id,
            role="system",
            content="You are a helpful AI assistant. When users tell you information about themselves (like their name), remember it and use it in your responses when appropriate."
        )
        db_session.add(system_message)
        
        db_session.commit()
        return chat_session.id
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

def get_all_chat_sessions():
    """Get all chat sessions."""
    db_session = Session()
    try:
        return [session.to_dict() for session in db_session.query(ChatSession).order_by(ChatSession.created_at.desc()).all()]
    finally:
        db_session.close()

def get_chat_session(session_id):
    """Get a specific chat session by ID."""
    db_session = Session()
    try:
        return db_session.query(ChatSession).filter(ChatSession.id == session_id).first()
    finally:
        db_session.close()

def update_chat_name(session_id, new_name):
    """Update the name of a chat session."""
    db_session = Session()
    try:
        chat_session = db_session.query(ChatSession).filter(ChatSession.id == session_id).first()
        if chat_session:
            chat_session.name = new_name
            db_session.commit()
            return True
        return False
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

def delete_chat_session(session_id):
    """Delete a chat session and all its messages."""
    db_session = Session()
    try:
        chat_session = db_session.query(ChatSession).filter(ChatSession.id == session_id).first()
        if chat_session:
            db_session.delete(chat_session)
            db_session.commit()
            return True
        return False
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

def get_messages_for_session(session_id):
    """Get all messages for a specific chat session."""
    db_session = Session()
    try:
        messages = db_session.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        return [message.to_dict() for message in messages]
    finally:
        db_session.close()

def add_message_to_session(session_id, role, content=None, image_path=None):
    """Add a new message to a chat session."""
    db_session = Session()
    try:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            image_path=image_path
        )
        db_session.add(message)
        db_session.commit()
        return message.id
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

def save_image(image_data, session_id):
    """Save an image to disk and return the path."""
    # Create directory if it doesn't exist
    image_dir = f"db/images/{session_id}"
    os.makedirs(image_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{image_dir}/{timestamp}.png"
    
    # Save the image
    with open(filename, 'wb') as f:
        f.write(image_data.getvalue())
    
    return filename
