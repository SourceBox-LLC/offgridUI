import streamlit as st
from model import generate_response
import database as db
import os
import re
import subprocess
import platform

st.title("OffGrid AI")
st.subheader("private, local, yours")
st.markdown("---")

# Custom CSS for styling the <think> content
st.markdown("""
<style>
.thinking-content {
    background-color: #f0f7fb;
    border-left: 5px solid #2196F3;
    padding: 10px;
    margin: 10px 0;
    color: #555;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

# Function to process message content for <think> tags
def process_message_content(content):
    """Process message content to style <think> tags"""
    if not content:
        return content
    
    # Check if there's a think tag
    think_pattern = r'<think>(.*?)</think>'
    match = re.search(think_pattern, content, re.DOTALL)
    
    if match:
        # Extract thinking content and regular content
        thinking_content = match.group(1).strip()
        
        # Replace the <think> tags with styled div
        styled_content = re.sub(
            think_pattern,
            r'<div class="thinking-content">\1</div>',
            content,
            flags=re.DOTALL
        )
        
        return styled_content
    
    return content

# Function to start the Ollama server
def launch_ollama_server():
    system = platform.system()
    
    try:
        if system == "Windows":
            # For Windows, open a new PowerShell window and run ollama serve
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-Command", "ollama serve"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return True, "Launched Ollama server in a new window."
        elif system == "Darwin":  # macOS
            # For macOS, open a new Terminal window and run ollama serve
            applescript = f'''
            tell application "Terminal"
                do script "ollama serve"
                activate
            end tell
            '''
            subprocess.run(["osascript", "-e", applescript])
            return True, "Launched Ollama server in a new Terminal window."
        elif system == "Linux":
            # For Linux, try to open a new terminal window (different distros use different terminal apps)
            # Try common terminal emulators
            terminals = ["gnome-terminal", "konsole", "xterm", "xfce4-terminal"]
            terminal_found = False
            
            for term in terminals:
                try:
                    # Check if the terminal exists by running 'which'
                    subprocess.run(["which", term], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Launch the terminal with ollama serve
                    subprocess.Popen([term, "-e", "ollama serve"])
                    terminal_found = True
                    break
                except subprocess.CalledProcessError:
                    continue
            
            if terminal_found:
                return True, "Launched Ollama server in a new terminal window."
            else:
                return False, "Could not find a suitable terminal emulator. Please open a terminal and run 'ollama serve' manually."
        else:
            return False, f"Unsupported operating system: {system}"
    except Exception as e:
        return False, f"Error launching Ollama server: {str(e)}"

# Initialize app state
if "current_session_id" not in st.session_state:
    # Create a new session if none exists yet
    sessions = db.get_all_chat_sessions()
    if not sessions:
        # No sessions exist in the database, create one
        new_session_id = db.create_new_chat_session("New Chat")
        st.session_state.current_session_id = new_session_id
    else:
        # Use the most recent session
        st.session_state.current_session_id = sessions[0]["id"]

# Load messages for the current session from database
def load_messages_from_db():
    messages = db.get_messages_for_session(st.session_state.current_session_id)
    return messages

# Display chat history for current session
messages = load_messages_from_db()
for message in messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if "content" in message:
                # Process content for <think> tags
                processed_content = process_message_content(message["content"])
                st.markdown(processed_content, unsafe_allow_html=True)
            if "image" in message:
                st.image(message["image"])

# Handle user input
prompt = st.chat_input(
    "Say something and/or attach an image",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if prompt:
    # Display user message
    with st.chat_message("user"):
        if prompt.text:
            # Process content for <think> tags when displaying
            processed_content = process_message_content(prompt.text)
            st.markdown(processed_content, unsafe_allow_html=True)
            # Create user message (store original content)
            user_content = prompt.text
        else:
            user_content = ""
            
        # Handle image
        image_path = None
        if prompt["files"]:
            st.image(prompt["files"][0])
            # Save image to disk
            image_path = db.save_image(prompt["files"][0], st.session_state.current_session_id)
    
    # Add user message to database
    db.add_message_to_session(
        st.session_state.current_session_id, 
        "user", 
        content=user_content, 
        image_path=image_path
    )
    
    # Get conversation history for model
    conversation = []
    for m in messages:
        if "content" in m:
            conversation.append({"role": m["role"], "content": m["content"]})
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(user_content, conversation)
            # Process response for <think> tags
            processed_response = process_message_content(response)
            st.markdown(processed_response, unsafe_allow_html=True)
    
    # Add AI response to database
    db.add_message_to_session(
        st.session_state.current_session_id, 
        "assistant", 
        content=response
    )
    
    # Refresh the page to show updated messages
    st.rerun()

with st.sidebar:
    st.title("Chat Sessions")
    
    # Get all sessions
    sessions = db.get_all_chat_sessions()
    
    # New chat button
    if st.button("New Chat", key="new_chat"):
        new_session_id = db.create_new_chat_session()
        st.session_state.current_session_id = new_session_id
        st.session_state.editing_chat_name = None
        st.rerun()
    
    # Display chat sessions
    st.write("Your conversations:")
    for session in sessions:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        # Check if we're editing this chat's name
        is_editing = st.session_state.get("editing_chat_name") == session["id"]
        is_active = session["id"] == st.session_state.current_session_id
        
        # Display chat name (editable or clickable)
        with col1:
            if is_editing:
                new_name = st.text_input(
                    "Edit name",
                    value=session["name"],
                    key=f"edit_name_{session['id']}"
                )
                if st.button("Save", key=f"save_{session['id']}"):
                    db.update_chat_name(session["id"], new_name)
                    st.session_state.editing_chat_name = None
                    st.rerun()
            else:
                # Make the button look like a link if it's not the active session
                if is_active:
                    st.markdown(f"**{session['name']}**")
                else:
                    if st.button(session["name"], key=f"session_{session['id']}"):
                        st.session_state.current_session_id = session["id"]
                        st.session_state.editing_chat_name = None
                        st.rerun()
        
        # Edit button
        with col2:
            if not is_editing:
                if st.button("✏️", key=f"edit_{session['id']}"):
                    st.session_state.editing_chat_name = session["id"]
                    st.rerun()
        
        # Delete button
        with col3:
            if st.button("🗑️", key=f"delete_{session['id']}"):
                # Confirm deletion
                st.session_state[f"confirm_delete_{session['id']}"] = True
                st.rerun()
        
        # Confirmation for deletion
        if st.session_state.get(f"confirm_delete_{session['id']}", False):
            st.warning("Are you sure you want to delete this chat?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes", key=f"confirm_yes_{session['id']}"):
                    # If we're deleting the current session, switch to another one
                    if session["id"] == st.session_state.current_session_id:
                        other_sessions = [s for s in sessions if s["id"] != session["id"]]
                        if other_sessions:
                            st.session_state.current_session_id = other_sessions[0]["id"]
                        else:
                            # Create a new session if there are no others
                            new_id = db.create_new_chat_session()
                            st.session_state.current_session_id = new_id
                    
                    # Delete the session
                    db.delete_chat_session(session["id"])
                    st.session_state.pop(f"confirm_delete_{session['id']}", None)
                    st.rerun()
            with col2:
                if st.button("No", key=f"confirm_no_{session['id']}"):
                    st.session_state.pop(f"confirm_delete_{session['id']}", None)
                    st.rerun()
    
    st.markdown("---")
    
    # Model selection
    model_option = st.text_input("Model", value="deepseek-r1")
    st.session_state['model_option'] = model_option
    
    # Launch Ollama server button
    if st.button("Launch Local Server"):
        success, message = launch_ollama_server()
        if success:
            st.success(message)
        else:
            st.error(message)