from openai import OpenAI
import logging
import time

def call_openai_llm(prompt, api_key, max_retries=3, retry_delay=2, conversation_history=None):
    """
    Call the OpenAI LLM API with proper error handling and retries.
    
    Args:
        prompt (str): The current prompt to send to the LLM
        api_key (str): The OpenAI API key
        max_retries (int): Maximum number of retries on failure
        retry_delay (int): Delay between retries in seconds
        conversation_history (list): List of previous messages in the conversation
        
    Returns:
        str: The LLM response text
    """
    if not api_key:
        raise ValueError("API key is required to call the LLM")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Prepare messages array for the API call
    messages = []
    
    # Add conversation history if provided
    if conversation_history and isinstance(conversation_history, list):
        messages.extend(conversation_history)
    
    # Add the current user prompt
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Set up retry mechanism
    retries = 0
    while retries <= max_retries:
        try:
            # Call the API with the full conversation history
            response = client.chat.completions.create(
                model="o3-mini",
                messages=messages,
                reasoning_effort="medium"
            )
            
            # Return the response content
            return response.choices[0].message.content
        
        except Exception as e:
            retries += 1
            logging.error(f"API call failed (attempt {retries}/{max_retries+1}): {str(e)}")
            
            # If we've reached max retries, raise the exception
            if retries > max_retries:
                raise Exception(f"Failed to get response from OpenAI API after {max_retries+1} attempts: {str(e)}")
            
            # Otherwise wait and retry
            time.sleep(retry_delay)
    
    # This should never be reached due to the exception in the loop
    return "I'm sorry, I couldn't process your request at this time."
