import streamlit as st
from openai import OpenAI
import os
import json
import time
from dotenv import load_dotenv
load_dotenv()

# Set page config
st.set_page_config(
    page_title="RunPod Chat Interface",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize stats with default values from environment
if 'stats' not in st.session_state:
    st.session_state.stats = {
        "execution_time": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "model_name": os.getenv("MODEL_NAME", "Not set"),
        "last_response": ""
    }

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
    Get streaming response from the RunPod endpoint using OpenAI compatibility layer
    """
    try:
        # Record start time
        start_time = time.time()
        
        # Format the prompt
        formatted_prompt = format_prompt(messages)
        print("Debug - Formatted prompt:", formatted_prompt)
        
        # Create a completion with streaming enabled
        response_stream = client.completions.create(
            model=model_name,
            prompt=formatted_prompt,
            temperature=temperature,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["Human:", "\n\n"],
            stream=True  # Enable streaming
        )
        
        # Initialize the placeholder for streaming text
        response_placeholder = st.empty()
        collected_chunks = []
        collected_messages = []
        full_response = ""
        
        # Process the streaming response
        for chunk in response_stream:
            if hasattr(chunk, 'model_dump'):
                chunk_dict = chunk.model_dump()
            elif isinstance(chunk, dict):
                chunk_dict = chunk
            else:
                chunk_dict = json.loads(str(chunk))
            
            collected_chunks.append(chunk_dict)
            chunk_message = ""
            
            if 'choices' in chunk_dict and chunk_dict['choices']:
                choice = chunk_dict['choices'][0]
                if isinstance(choice, dict):
                    if 'text' in choice:
                        chunk_message = choice['text']
                    elif 'delta' in choice and 'content' in choice['delta']:
                        chunk_message = choice['delta']['content']
            
            collected_messages.append(chunk_message)
            full_response = ''.join(collected_messages)
            response_placeholder.markdown(full_response + "▌")
        
        # Replace the blinking cursor with the final response
        response_placeholder.markdown(full_response)
        
        # Calculate execution time
        execution_time = int((time.time() - start_time) * 1000)
        
        # Calculate token counts
        prompt_tokens = len(formatted_prompt.split())
        completion_tokens = len(full_response.split())
        
        # Update stats
        st.session_state.stats.update({
            "execution_time": execution_time,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "model_name": model_name,
            "last_response": full_response
        })
        
        return full_response
            
    except Exception as e:
        error_msg = str(e)
        print(f"Debug - Error in get_chatbot_response: {error_msg}")
        st.error(f"Error: {error_msg}")
        
        # Update stats even in case of error
        st.session_state.stats.update({
            "execution_time": int((time.time() - start_time) * 1000),
            "prompt_tokens": len(formatted_prompt.split()),
            "completion_tokens": 0,
            "total_tokens": len(formatted_prompt.split()),
            "model_name": model_name,
            "last_response": f"Error: {error_msg}"
        })
        
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

# Sidebar with stats
with st.sidebar:
    st.title("RunPod Stats")
    st.write("### Current Response Stats")
    
    # Model information
    st.write("#### 🤖 Model")
    if 'stats' in st.session_state and st.session_state.stats['model_name']:
        st.info(st.session_state.stats['model_name'])
    else:
        st.info(os.getenv("MODEL_NAME", "Not set"))
    
    # Timing information
    st.write("#### ⏱️ Timing")
    execution_time = st.session_state.stats.get('execution_time', 0)
    st.info(f"{execution_time}ms")
    if execution_time > 1000:
        st.write(f"({execution_time/1000:.1f} seconds)")
    
    # Token information with better formatting
    st.write("#### 🔤 Token Usage")
    col1, col2 = st.columns(2)
    with col1:
        prompt_tokens = st.session_state.stats.get('prompt_tokens', 0)
        st.metric(
            "Prompt", 
            value=prompt_tokens,
            delta=None,
            help="Number of tokens in the prompt"
        )
    with col2:
        completion_tokens = st.session_state.stats.get('completion_tokens', 0)
        st.metric(
            "Completion", 
            value=completion_tokens,
            delta=None,
            help="Number of tokens in the completion"
        )
    
    total_tokens = st.session_state.stats.get('total_tokens', 0)
    st.metric(
        "Total Tokens", 
        value=total_tokens,
        delta=None,
        help="Total number of tokens used"
    )
    
    # Debug information
    with st.expander("🔍 Debug Info", expanded=True):
        st.write("**Raw stats:**")
        st.json(st.session_state.stats)
        st.write("**Environment:**")
        st.write(f"- MODEL_NAME: {os.getenv('MODEL_NAME')}")
        st.write(f"- ENDPOINT_ID: {os.getenv('RUNPOD_ENDPOINT_ID')}")
        st.write("**Session State:**")
        st.write("- Stats initialized:", 'stats' in st.session_state)
        st.write("- Chat history length:", len(st.session_state.chat_history))

# Main chat interface
st.title("🤖 RunPod Chat Interface")

# Initialize the OpenAI Client
endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
base_url = f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1"

try:
    client = OpenAI(
        api_key=os.getenv("RUNPOD_TOKEN"),
        base_url=base_url
    )
    print(f"Debug - OpenAI client initialized with base_url: {base_url}")
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to ask?"):
    if client is None:
        st.error("OpenAI client is not initialized. Please check your configuration.")
    else:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare messages for the model
        messages = [
            {
                "role": "system",
                "content": "You are a helpful and knowledgeable AI assistant. Answer questions accurately and concisely."
            }
        ] + st.session_state.chat_history
        
        # Get model response with streaming
        with st.chat_message("assistant"):
            response = get_chatbot_response(client, os.getenv("MODEL_NAME"), messages)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Force a rerun to update the sidebar
        st.experimental_rerun() 