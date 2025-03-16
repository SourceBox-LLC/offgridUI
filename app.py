import streamlit as st
import os
from openai_llm import call_openai_llm
from ollama_llm import call_ollama_llm
from replicate_llms import call_replicate_model
from PIL import Image
import io
import base64
import uuid
from model import ChatDatabase

# Optional imports for file handling - will be imported dynamically when needed
# import pandas as pd
# import PyPDF2
# import docx

# Initialize database
db = ChatDatabase()

# Set page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background and container styles */
    .main {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Inter', sans-serif;
    }
    
    /* Container styling */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Chat containers */
    .chat-container {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #313244;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        font-size: 16px;
        line-height: 1.5;
    }
    
    .user-message {
        background-color: #313244;
        color: #cdd6f4;
        margin-left: 2rem;
        border-top-left-radius: 2px;
    }
    
    .assistant-message {
        background-color: #45475a;
        color: #cdd6f4;
        margin-right: 2rem;
        border-top-right-radius: 2px;
    }
    
    /* Avatar styling */
    .avatar-container {
        padding: 0.5rem;
        background-color: #1e1e2e;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        font-size: 2rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        margin: 0 auto;
    }
    
    .user-avatar {
        background-color: #89b4fa;
        color: #1e1e2e;
    }
    
    .assistant-avatar {
        background-color: #f38ba8;
        color: #1e1e2e;
    }
    
    /* Title and subtitle styling */
    .title {
        text-align: center;
        color: #cdd6f4;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #a6adc8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Input fields */
    .stTextInput, .stTextArea, div[data-baseweb="input"] input {
        background-color: #313244 !important;
        color: #cdd6f4 !important;
        border: 1px solid #45475a !important;
        border-radius: 8px !important;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #cba6f7 !important;
        color: #1e1e2e !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background-color: #f5c2e7 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Chat input styling */
    .stChatInput {
        border-radius: 16px !important;
        overflow: hidden !important;
    }
    
    /* Make sidebar more modern */
    [data-testid="stSidebar"] {
        background-color: #181825 !important;
        border-right: 1px solid #313244 !important;
        padding: 1rem !important;
    }
    
    /* Headers in sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #cba6f7 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar divider */
    [data-testid="stSidebar"] hr {
        border-color: #313244 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Images */
    img {
        border-radius:.5rem !important;
        margin: 1rem 0 !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #181825;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #45475a;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #cba6f7;
    }
    
    /* Error messages */
    .stAlert {
        background-color: #313244 !important;
        color: #f38ba8 !important;
        border-left-color: #f38ba8 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #313244 !important;
        color: #fab387 !important;
        border-left-color: #fab387 !important;
    }
    
    /* Spinner */
    .stSpinner > div > div {
        border-color: #cba6f7 transparent transparent !important;
    }
    
    /* Conversation selector styling */
    .conversation-selector {
        background-color: #313244;
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for API key and current conversation
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Initialize or get the current conversation ID
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = db.generate_conversation_id()

# Initialize or get the offgrid state
if "offgrid" not in st.session_state:
    st.session_state.offgrid = False

# Main app layout
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("<h1 class='title'>AI Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your intelligent chat companion</p>", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("<h2 style='color: #cba6f7;'>Settings</h2>", unsafe_allow_html=True)
    on = st.toggle("Go offgrid")

    #toggle on and offgrid via session state
    if on:
        st.session_state.offgrid = True
    else:
        st.session_state.offgrid = False
    
    if st.session_state.offgrid == False:
        option = st.selectbox(
            "Choose your online AI model",
            ("OpenAI/o3-mini", "Replicate")
        )
        st.write("Current model:", option)

        if option == "OpenAI/o3-mini":
            st.session_state.model = "o3-mini"
        elif option == "Replicate":
            st.session_state.model = "replicate"
        else:
            st.session_state.model = "local"

        if st.session_state.model == "o3-mini":
            api_key = st.text_input("OpenAI API Key", value=st.session_state.get("api_key", ""), type="password", key="o3-mini-api-key")
            st.link_button("Get API key", "https://platform.openai.com/api-keys")

        elif st.session_state.model == "replicate":
            api_key = st.text_input("Replicate API Key", value=st.session_state.get("api_key", ""), type="password", key="replicate-api-key")
            st.link_button("Get API key", "https://replicate.com/account/api-tokens")
            
            # Text input for model ID
            replicate_model_id = st.text_input(
                "Enter any Replicate Model ID", 
                value=st.session_state.get("replicate_model_id", "meta/meta-llama-3-70b-instruct")
            )
            st.session_state.replicate_model_id = replicate_model_id
            
            # Help text
            st.markdown("*Find models at [replicate.com/collections/language-models](https://replicate.com/collections/language-models)*")
        
        else:
            st.session_state.model = "local"
            api_key = None
        
        if api_key:
            st.session_state.api_key = api_key
    else:
        # Offline mode - Ollama
        st.session_state.model = "local"
        
        # Text input for Ollama model ID instead of select box
        ollama_model = st.text_input(
            "Enter any local Ollama model name", 
            value=st.session_state.get("model_option", "deepseek-r1")
        )
        st.session_state.model_option = ollama_model
        st.write(f"Using local model: {ollama_model}")
        
        # Help text
        st.markdown("*Common models: llama3, deepseek-r1, mistral, phi3*")
    
    st.divider()
    
    # Get all conversations from database
    try:
        conversations = db.get_all_conversations()
        conversation_ids = [conv['conversation_id'] for conv in conversations]
        
        # Add option to create a new conversation
        st.markdown("<h3 style='color: #cba6f7;'>Conversations</h3>", unsafe_allow_html=True)
        
        if st.button("New Conversation", use_container_width=True):
            st.session_state.current_conversation_id = db.generate_conversation_id()
            st.rerun()
        
        # Show existing conversations
        if conversations:
            st.markdown("<p>Select a conversation:</p>", unsafe_allow_html=True)
            for conv in conversations:
                conv_id = conv['conversation_id']
                # Get the first message to use as a title
                messages = db.get_conversation_messages(conv_id)
                title = "Conversation"
                if messages:
                    # Use first few characters of first message as title
                    first_msg = messages[0]['content']
                    title = first_msg[:20] + "..." if len(first_msg) > 20 else first_msg
                
                if st.button(f"{title}", key=conv_id, use_container_width=True):
                    st.session_state.current_conversation_id = conv_id
                    st.rerun()
        
        st.divider()
        
        if st.button("Clear Current Conversation", use_container_width=True):
            # Delete the current conversation from the database
            db.delete_conversation(st.session_state.current_conversation_id)
            # Create a new conversation ID
            st.session_state.current_conversation_id = db.generate_conversation_id()
            st.rerun()
    except Exception as e:
        st.error(f"Error loading conversations: {str(e)}")

    # Add user guide
    st.sidebar.markdown("---")
    with st.sidebar.expander("How to use"):
        st.markdown("""
        ### AI Assistant User Guide

        **Getting Started**
        1. Select a model from the dropdown menu:
           - **OpenAI/o3-mini**: Uses OpenAI's models (requires API key)
           - **Replicate**: Uses any model from Replicate (requires API key)
           - Or toggle "Go offgrid" to use Ollama's local models

        **Using API-based Models (OpenAI & Replicate)**
        1. Obtain an API key:
           - [OpenAI API key](https://platform.openai.com/api-keys)
           - [Replicate API key](https://replicate.com/account/api-tokens)
        2. Enter your API key in the sidebar
        3. For Replicate, you can specify any model ID (default: meta/meta-llama-3-70b-instruct)

        **Using Local Models (Ollama)**
        1. Toggle "Go offgrid" in the sidebar
        2. [Install Ollama](https://ollama.com/download) on your computer
        3. Pull models using `ollama pull modelname` in your terminal
        4. Enter the model name in the text field (e.g., llama3, deepseek-r1)
        5. No API key required - runs completely locally!

        **Document Analysis**
        1. Upload documents using the file uploader (supports PDF, Excel, CSV, Word, TXT)
        2. Type a query about the document (e.g., "summarize this")
        3. The AI will analyze the document content and respond to your query
        4. For PDFs: Some scanned documents may require OCR before uploading

        **Managing Conversations**
        1. Start a new conversation with the "New Conversation" button
        2. Switch between conversations using the sidebar
        3. Clear the current conversation with "Clear Current Conversation"

        **Troubleshooting**
        - **"Failed to connect to Ollama server"**: Ensure Ollama is running on your computer
        - **PDF extraction issues**: Try using an OCR tool on scanned PDFs first
        - **API errors**: Check that your API key is valid and has sufficient credits
        - **Model not found**: For Replicate/Ollama, verify the model name is correct
        """)
    
    

# Display chat messages from the database
try:
    messages = db.get_conversation_messages(st.session_state.current_conversation_id)
    
    for message in messages:
        role = message["role"]
        content = message["content"]
        image_data = message.get("image")
        
        # Determine message styling based on role
        message_class = "user-message" if role == "user" else "assistant-message"
        avatar_class = "user-avatar" if role == "user" else "assistant-avatar"
        avatar = "👤" if role == "user" else "🤖"
        
        # Container for the message
        with st.container():
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.markdown(f"<div class='avatar-container {avatar_class}'>{avatar}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='chat-message {message_class}'>{content}</div>", unsafe_allow_html=True)
                
                # Display image if present
                if image_data:
                    try:
                        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                        st.image(image, use_column_width=True)
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading messages: {str(e)}")

# User input section
with st.container():
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a document to analyze (xlsx, csv, pdf, docx, txt)", type=["xlsx", "xls", "csv", "docx", "doc", "txt", "pdf"], label_visibility="visible")
    
    prompt = st.chat_input("Type your message here...")
    
    if prompt:
        # Get the current conversation ID
        conversation_id = st.session_state.current_conversation_id
        
        # Only store image data for actual images, not documents
        image_data = None
        
        # If there's an uploaded file, add information about it to the prompt
        user_message = prompt
        if uploaded_file:
            file_name = uploaded_file.name
            user_message = f"[File attached: {file_name}]\n\n{prompt}"
        
        # Save user message to database without attaching the file
        db.save_message("user", user_message, conversation_id, image_data)
        
        # Check if API key is provided
        if st.session_state.api_key:
            try:
                # Display a spinner while waiting for the response
                with st.spinner("AI is thinking..."):
                    # Get previous messages in the conversation for context
                    previous_messages = db.get_conversation_messages(conversation_id)
                    
                    # Format messages for the OpenAI API format
                    conversation_history = []
                    for msg in previous_messages:
                        # Skip the current message which we already added
                        if msg["role"] == "user" and msg["content"] == user_message:
                            continue
                            
                        # Format message for the API
                        conversation_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    # Create a prompt that includes image description if present
                    llm_prompt = prompt
                    if uploaded_file:
                        # Read file contents based on file type
                        file_content = ""
                        file_type = uploaded_file.type
                        try:
                            if file_type == "text/plain" or uploaded_file.name.endswith(".txt"):
                                # For text files
                                file_content = uploaded_file.getvalue().decode("utf-8")
                            elif file_type == "application/pdf" or uploaded_file.name.endswith(".pdf"):
                                # For PDF files - requires PyPDF2
                                import PyPDF2
                                from io import BytesIO
                                
                                print(f"Processing PDF file: {uploaded_file.name}, Size: {len(uploaded_file.getvalue())} bytes")
                                try:
                                    pdf_file = BytesIO(uploaded_file.getvalue())
                                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                                    
                                    # Check if the PDF has any pages
                                    if len(pdf_reader.pages) == 0:
                                        file_content = "[PDF appears to be empty or corrupted]"
                                    else:
                                        # Extract text from each page
                                        for page_num in range(len(pdf_reader.pages)):
                                            page_text = pdf_reader.pages[page_num].extract_text()
                                            if page_text.strip():  # Check if extracted text is not empty
                                                file_content += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
                                        
                                        # If no text was extracted (possibly a scanned/image PDF)
                                        if not file_content.strip():
                                            # Try to get metadata
                                            metadata = ""
                                            if pdf_reader.metadata:
                                                for key, value in pdf_reader.metadata.items():
                                                    if key and value and str(value).strip():
                                                        clean_key = str(key).replace('/', '')
                                                        metadata += f"{clean_key}: {value}\n"
                                            
                                            if metadata:
                                                file_content = f"[This appears to be a scanned or image-based PDF without extractable text. PDF Metadata:\n{metadata}\n\nConsider using an OCR tool to extract text from the PDF before uploading.]"
                                            else:
                                                file_content = "[This appears to be a scanned or image-based PDF without extractable text. Consider using an OCR tool to extract text from the PDF before uploading.]"
                                except Exception as pdf_error:
                                    print(f"PDF extraction error: {str(pdf_error)}")
                                    # Try to get basic information about the PDF
                                    try:
                                        file_size = len(uploaded_file.getvalue())
                                        file_content = f"[Error extracting PDF content: {str(pdf_error)}. File size: {file_size} bytes. The PDF might be password-protected, corrupted, or in an unsupported format.]"
                                    except:
                                        file_content = f"[Error extracting PDF content: {str(pdf_error)}]"
                            elif file_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             "application/vnd.ms-excel"] or uploaded_file.name.endswith((".xlsx", ".xls")):
                                # For Excel files - requires pandas
                                import pandas as pd
                                df = pd.read_excel(uploaded_file)
                                file_content = df.to_string()
                            elif file_type == "text/csv" or uploaded_file.name.endswith(".csv"):
                                # For CSV files - requires pandas
                                import pandas as pd
                                df = pd.read_csv(uploaded_file)
                                file_content = df.to_string()
                            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                           "application/msword"] or uploaded_file.name.endswith((".docx", ".doc")):
                                # For Word files - requires python-docx
                                import docx
                                from io import BytesIO
                                doc = docx.Document(BytesIO(uploaded_file.getvalue()))
                                file_content = "\n".join([para.text for para in doc.paragraphs])
                            else:
                                # For other file types, try to read as text or inform user
                                try:
                                    file_content = uploaded_file.getvalue().decode("utf-8")
                                except UnicodeDecodeError:
                                    file_content = "[File content could not be extracted. Unsupported file type.]"
                            
                            # Limit content length to avoid overwhelming the models
                            if len(file_content) > 10000:
                                file_content = file_content[:10000] + "\n[Content truncated due to length...]"
                                
                            # Create the enhanced prompt with file content
                            llm_prompt = f"""The user has uploaded a file with the following content:

FILE CONTENT:
{file_content}

USER QUERY:
{prompt}

Please respond to the user's query based on the file content."""
                        except Exception as e:
                            llm_prompt = f"The user has uploaded a file, but I couldn't extract its contents due to error: {str(e)}. User's message: {prompt}"
                    
                    # Call the LLM with conversation history for context
                    if st.session_state.offgrid == False:
                        if st.session_state.model == "o3-mini":
                            response = call_openai_llm(
                                llm_prompt, 
                                st.session_state.api_key,
                                conversation_history=conversation_history
                            )
                        elif st.session_state.model == "replicate":
                            response = call_replicate_model(
                                llm_prompt,
                                api_key=st.session_state.api_key,
                                model_id=st.session_state.replicate_model_id,
                                conversation_history=conversation_history
                            )
                    else:
                        response = call_ollama_llm(
                            llm_prompt, 
                            conversation_history=conversation_history
                        )
                    
                    # Save assistant's response to database
                    db.save_message("assistant", response, conversation_id)
                    
                    # Rerun to update the UI with the new message
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            if st.session_state.model == "o3-mini":
                st.warning("Please enter your OpenAI API key in the sidebar to get AI responses.")
            elif st.session_state.model == "replicate":
                st.warning("Please enter your Replicate API key in the sidebar to get AI responses.")
            else:
                st.warning("Please select a model and enter the appropriate API key in the sidebar.")
            st.rerun()

