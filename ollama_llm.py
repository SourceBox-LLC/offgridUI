import requests
import json, re
import streamlit as st
import logging
import time

OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"

def ollama_chat_request(prompt, conversation=None, model=None):
    """
    Sends a prompt to the Ollama API and returns the response content.
    """
    # Use the model selected in the sidebar if available, otherwise use the default
    if model is None:
        model = st.session_state.get('model_option', 'deepseek-r1')
    
    if conversation is None:
        conversation = []

    # Create a full conversation history to send to Ollama
    messages = conversation.copy()
    # Add the current prompt as the last user message
    messages.append({"role": "user", "content": prompt})
    
    # Debug the conversation being sent
    print(f"Sending conversation to Ollama: {json.dumps(messages, indent=2)}")
    
    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_ENDPOINT, json=data)
        response_json = response.json()
        # Debug the response received
        print(f"Response from Ollama: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print("Error: Received an invalid JSON response.")
        return "I received an invalid response from the AI model. Please try again."
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the Ollama server.")
        return "Failed to connect to the Ollama server. Please make sure it's running at " + OLLAMA_ENDPOINT
    except Exception as e:
        print(f"Error making the request: {e}")
        return f"Error when making request to the AI model: {str(e)}"

    try:
        content = response_json["message"]["content"].strip()
        return content
    except KeyError:
        print("Error: 'message' key not found in the response:")
        print(response_json)
        return "The AI model returned an unexpected response. Please try again."


def call_ollama_llm(prompt, max_retries=3, retry_delay=2, conversation_history=None):
    """
    Generates a response based on the provided prompt and conversation history.
    Function signature matches call_openai_llm (except for api_key) for compatibility.
    
    Args:
        prompt (str): The current prompt to send to the LLM
        max_retries (int): Maximum number of retries on failure
        retry_delay (int): Delay between retries in seconds
        conversation_history (list): List of previous messages in the conversation
        
    Returns:
        str: The LLM-generated response as a string
    """
    if prompt == "" or prompt is None:
        prompt = "Hello"

    # Get the selected model from session state if available
    model = st.session_state.get('model_option', 'deepseek-r1')
    
    # Set up retry mechanism
    retries = 0
    while retries <= max_retries:
        try:
            response = ollama_chat_request(prompt, conversation_history, model)
            
            # If the response is None or empty, provide a fallback response
            if response is None or response.strip() == "":
                return "I apologize, but I couldn't generate a proper response. Please try again."
                
            return response.strip()
            
        except Exception as e:
            retries += 1
            logging.error(f"API call failed (attempt {retries}/{max_retries+1}): {str(e)}")
            
            # If we've reached max retries, raise the exception
            if retries > max_retries:
                raise Exception(f"Failed to get response from Ollama API after {max_retries+1} attempts: {str(e)}")
            
            # Otherwise wait and retry
            time.sleep(retry_delay)
    
    # This should never be reached due to the exception in the loop
    return "I'm sorry, I couldn't process your request at this time."


if __name__ == "__main__":
    print(call_ollama_llm("Hello"))
