from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
import base64

# Create the base class for our models
Base = declarative_base()

# Define the Message model
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    conversation_id = Column(String(100), nullable=False)  # To group messages by conversation
    has_image = Column(Boolean, default=False)
    
    # Relationship with Image model
    image = relationship("Image", uselist=False, back_populates="message", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert the message to a dictionary for the app"""
        result = {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "has_image": self.has_image
        }
        
        # Include image data if present
        if self.has_image and self.image:
            result["image"] = self.image.image_data
            
        return result

# Define the Image model (for storing base64 encoded images)
class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    image_data = Column(Text, nullable=False)  # Base64 encoded image
    
    # Relationship with Message model
    message = relationship("Message", back_populates="image")

# Database setup function
def init_db(db_path='chat_history.db'):
    """Initialize the database and create tables"""
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    # Create SQLite database engine
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return engine, Session

# Database operations
class ChatDatabase:
    def __init__(self, db_path='chat_history.db'):
        """Initialize the database connection"""
        self.engine, self.Session = init_db(db_path)
        
    def save_message(self, role, content, conversation_id, image_data=None):
        """Save a message to the database"""
        session = self.Session()
        try:
            # Create message
            has_image = image_data is not None
            message = Message(
                role=role,
                content=content,
                conversation_id=conversation_id,
                has_image=has_image
            )
            
            session.add(message)
            session.flush()  # This generates an ID for the message
            
            # Add image if present
            if has_image:
                image = Image(
                    message_id=message.id,
                    image_data=image_data
                )
                message.image = image
                session.add(image)
                
            session.commit()
            return message.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_conversation_messages(self, conversation_id):
        """Get all messages for a specific conversation"""
        session = self.Session()
        try:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp).all()
            
            return [message.to_dict() for message in messages]
        finally:
            session.close()
    
    def get_all_conversations(self):
        """Get a list of all conversation IDs"""
        session = self.Session()
        try:
            # Get distinct conversation IDs and their most recent timestamp
            conversations = session.query(
                Message.conversation_id,
                # Get the max timestamp for each conversation
                func.max(Message.timestamp).label('last_updated')
            ).group_by(Message.conversation_id).all()
            
            return [
                {
                    'conversation_id': conv[0], 
                    'last_updated': conv[1].isoformat()
                } 
                for conv in conversations
            ]
        finally:
            session.close()
    
    def delete_conversation(self, conversation_id):
        """Delete all messages in a conversation"""
        session = self.Session()
        try:
            # Find all messages in the conversation
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).all()
            
            # Delete each message (and associated images due to cascade)
            for message in messages:
                session.delete(message)
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
    
    def generate_conversation_id(self):
        """Generate a unique conversation ID"""
        import uuid
        return str(uuid.uuid4()) 