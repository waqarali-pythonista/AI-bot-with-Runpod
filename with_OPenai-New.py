from openai import OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv()

def validate_environment():
    """Validate environment variables are set correctly"""
    token = os.getenv("RUNPOD_TOKEN")
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    model_name = os.getenv("MODEL_NAME")
    
    errors = []
    
    if not token:
        errors.append("RUNPOD_TOKEN is not set")
    elif not (token.startswith("rp_") or token.startswith("rpa_")):
        errors.append("RUNPOD_TOKEN should start with 'rp_' or 'rpa_'. Please check your RunPod API key format.")
    
    if not endpoint_id:
        errors.append("RUNPOD_ENDPOINT_ID is not set")
    
    if not model_name:
        errors.append("MODEL_NAME is not set")
    
    return errors

def format_prompt(messages):
    """
    Format messages for Llama model in a simpler format
    """
    formatted_text = ""
    for message in messages:
        role = message["role"]
        content = message["content"]
        
        if role == "system":
            formatted_text += f"{content}\n\n"
        elif role == "user":
            formatted_text += f"Human: {content}\n"
        elif role == "assistant":
            formatted_text += f"Assistant: {content}\n"
    
    formatted_text += "Assistant: "
    return formatted_text

def get_chatbot_response(client, model_name, messages, temperature=0.7):
    """
    Get response from the RunPod endpoint using OpenAI compatibility layer
    """
    try:
        # Format the prompt
        formatted_prompt = format_prompt(messages)
        print("\nDebug - Formatted prompt:", formatted_prompt)
        
        # Create a completion with specific parameters for Llama
        response = client.completions.create(
            model=model_name,
            prompt=formatted_prompt,
            temperature=temperature,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["Human:", "\n\n"],
            stream=False
        )
        
        print("\nDebug - Full response:", response)
        
        # Extract the response text
        if hasattr(response, 'choices') and response.choices:
            text = response.choices[0].text.strip()
            if text:
                return text
        
        # Fallback to dictionary access if attribute access fails
        if isinstance(response, dict):
            if 'choices' in response and response['choices']:
                text = response['choices'][0].get('text', '').strip()
                if text:
                    return text
            elif 'output' in response:
                output = response['output']
                if isinstance(output, list) and output:
                    return str(output[0]).strip()
                return str(output).strip()
        
        print("\nDebug - Could not extract response content. Response structure:", response)
        return "No response generated"
            
    except Exception as e:
        error_msg = str(e)
        print(f"\nDebug - Error in get_chatbot_response: {error_msg}")
        if "401" in error_msg:
            return "Authentication failed. Please check your RunPod API token."
        elif "404" in error_msg:
            return "Endpoint not found. Please check your RUNPOD_ENDPOINT_ID."
        else:
            return f"Error: {error_msg}"

def get_available_models(client):
    """
    Get list of available models from the endpoint
    """
    try:
        models_response = client.models.list()
        return [model.id for model in models_response]
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            print("Authentication failed. Please check your RunPod API token.")
        elif "404" in error_msg:
            print("Endpoint not found. Please check your RUNPOD_ENDPOINT_ID.")
        else:
            print(f"Error getting models: {error_msg}")
        return []

def main():
    # Validate environment variables
    errors = validate_environment()
    if errors:
        print("Environment configuration errors:")
        for error in errors:
            print(f"- {error}")
        print("\nPlease fix these issues and try again.")
        return

    # Initialize the OpenAI Client with RunPod configuration
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    base_url = f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1"
    print(f"Connecting to endpoint: {base_url}")

    client = OpenAI(
        api_key=os.getenv("RUNPOD_TOKEN"),
        base_url=base_url
    )

    # Get available models
    print("\nFetching available models...")
    available_models = get_available_models(client)
    if available_models:
        print("Available models:", available_models)
    else:
        print("No models available or couldn't fetch models.")
        return

    # Your model name from environment variables
    model_name = os.getenv("MODEL_NAME")
    
    # Test message with a simpler format
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and knowledgeable AI assistant. Answer questions accurately and concisely."
        },
        {
            "role": "user",
            "content": "What is the capital of Italy?"
        }
    ]
    
    # Get response
    print(f"\nSending request to model: {model_name}")
    response = get_chatbot_response(client, model_name, messages)
    print("\nResponse:", response)

if __name__ == "__main__":
    main() 