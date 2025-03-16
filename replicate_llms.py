import replicate
import os
import time
import logging

# Set a placeholder API key - only used for testing



def call_replicate_model(prompt, api_key=None, model_id="meta/meta-llama-3-70b-instruct", max_retries=3, retry_delay=2, conversation_history=None, model_params=None):
    """
    Call any model via Replicate API with proper error handling and retries.
    
    Args:
        prompt (str): The current prompt to send to the LLM
        api_key (str): The Replicate API key (if provided, will override the environment variable)
        model_id (str): The Replicate model ID in format "owner/model" or "owner/model:version"
        max_retries (int): Maximum number of retries on failure
        retry_delay (int): Delay between retries in seconds
        conversation_history (list): List of previous messages in the conversation
        model_params (dict): Additional parameters specific to the model
        
    Returns:
        str: The LLM response text
    """
    # Set API key if provided (override environment variable)
    if api_key:
        os.environ["REPLICATE_API_TOKEN"] = api_key
    
    # Format messages for chat models
    system_message = "You are a helpful assistant"
    messages = []
    
    # First, extract system message if available
    if conversation_history and isinstance(conversation_history, list):
        for msg in conversation_history:
            if msg.get("role") == "system":
                system_message = msg.get("content", system_message)
                break
    
    # Add system message as the first message
    messages.append({"role": "system", "content": system_message})
    
    # Add conversation history
    if conversation_history and isinstance(conversation_history, list):
        for msg in conversation_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            # Skip system messages as we already added one
            if role != "system" and role in ["user", "assistant"]:
                messages.append({"role": role, "content": content})
    
    # Add the current prompt
    messages.append({"role": "user", "content": prompt})
    
    # Create default input parameters for most models
    input_params = {
        "prompt": prompt,
        "messages": messages,
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 1024
    }
    
    # If model is Mistral 7B, adjust parameters accordingly
    if "mistral" in model_id.lower():
        input_params = {
            "prompt": prompt,
            "temperature": 0.6,
            "top_p": 0.9,
            "max_length": 1024,
            "repetition_penalty": 1.0
        }
    # If model is Claude or Anthropic
    elif "anthropic" in model_id.lower():
        input_params = {
            "prompt": f"Human: {prompt}\n\nAssistant:",
            "temperature": 0.6,
            "max_tokens_to_sample": 1024
        }
    # If model is Stable Diffusion or other image model
    elif "stability" in model_id.lower():
        input_params = {
            "prompt": prompt,
            "width": 768,
            "height": 768,
            "num_outputs": 1
        }
    
    # Override with any custom model parameters
    if model_params and isinstance(model_params, dict):
        input_params.update(model_params)
    
    # Set up retry mechanism
    retries = 0
    full_response = ""
    
    while retries <= max_retries:
        try:
            # Collect the full response from the stream
            full_response = ""
            for event in replicate.stream(
                model_id,
                input=input_params
            ):
                # Handle ServerSentEvent objects properly by extracting data
                if hasattr(event, 'data'):
                    event_text = event.data
                else:
                    event_text = str(event)
                
                full_response += event_text
            
            return full_response.strip()
            
        except Exception as e:
            retries += 1
            logging.error(f"Replicate API call to {model_id} failed (attempt {retries}/{max_retries+1}): {str(e)}")
            
            # If we've reached max retries, raise the exception
            if retries > max_retries:
                raise Exception(f"Failed to get response from {model_id} after {max_retries+1} attempts: {str(e)}")
            
            # Otherwise wait and retry
            time.sleep(retry_delay)
    
    # This should never be reached due to the exception in the loop
    return "I'm sorry, I couldn't process your request at this time."

