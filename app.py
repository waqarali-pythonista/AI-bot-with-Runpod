import streamlit as st
import json
import time
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="RunPod Chat Interface",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv("RUNPOD_API_KEY")
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'stats' not in st.session_state:
    st.session_state.stats = {
        "execution_time": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }

def display_stats():
    """Function to display stats in the sidebar"""
    with st.sidebar:
        st.title("RunPod Stats")
        st.write("### Current Response Stats")
        
        # Timing information
        st.write("#### ⏱️ Timing")
        execution_time = st.session_state.stats["execution_time"]
        st.write(f"Total Time: {execution_time}ms")
        if execution_time > 1000:
            st.write(f"({execution_time/1000:.1f} seconds)")
        
        # Token information
        st.write("#### 🔤 Token Usage")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input", st.session_state.stats["input_tokens"])
        with col2:
            st.metric("Output", st.session_state.stats["output_tokens"])
        st.metric("Total Tokens", st.session_state.stats["total_tokens"])
        
        # Debug information
        with st.expander("🔍 Debug Info"):
            st.write("Raw stats:")
            st.json(st.session_state.stats)

# Display stats initially
display_stats()

# Main chat interface
st.title("🤖 RunPod Chat Interface")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if st.session_state.api_key:
    if prompt := st.chat_input("What would you like to ask?"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Create a placeholder for the assistant's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                start_time = time.time()
                
                # Prepare headers and data
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {st.session_state.api_key}'
                }
                
                data = {
                    'input': {
                        "prompt": prompt
                    }
                }
                
                # Make the request
                response = requests.post(
                    'https://api.runpod.ai/v2/tzwg1ryfn03n0t/run',
                    headers=headers,
                    json=data
                )
                
                result = response.json()
                
                if "error" in result:
                    full_response = f"Error: {result['error']}\nRaw response: {result.get('raw_response', 'No raw response')}"
                elif not result.get("id"):
                    full_response = "No job ID received in response"
                else:
                    job_id = result["id"]
                    # Check status until completed
                    while True:
                        status_response = requests.get(
                            f'https://api.runpod.ai/v2/tzwg1ryfn03n0t/status/{job_id}',
                            headers=headers
                        )
                        status = status_response.json()
                        
                        if "error" in status:
                            full_response = f"Error checking status: {status['error']}\nRaw response: {status.get('raw_response', 'No raw response')}"
                            break
                        
                        current_status = status.get("status")
                        
                        if current_status == "COMPLETED":
                            # Get the output data
                            output = status.get("output", [])
                            if isinstance(output, list) and len(output) > 0:
                                response_data = output[0]
                                
                                # Update stats
                                execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
                                usage_data = response_data.get("usage", {})
                                input_tokens = usage_data.get("input", 0)
                                output_tokens = usage_data.get("output", 0)
                                
                                st.session_state.stats.update({
                                    "execution_time": execution_time,
                                    "input_tokens": input_tokens,
                                    "output_tokens": output_tokens,
                                    "total_tokens": input_tokens + output_tokens
                                })
                                
                                # Get the response text
                                if isinstance(response_data, dict):
                                    # Try to get text from different possible locations
                                    if "text" in response_data:
                                        full_response = response_data["text"]
                                    elif "response" in response_data:
                                        full_response = response_data["response"]
                                    elif "choices" in response_data and len(response_data["choices"]) > 0:
                                        choice = response_data["choices"][0]
                                        if "text" in choice:
                                            full_response = choice["text"]
                                        elif "message" in choice:
                                            full_response = choice["message"]
                                        elif "content" in choice:
                                            full_response = choice["content"]
                                        elif "tokens" in choice:
                                            full_response = " ".join(choice["tokens"])
                                    else:
                                        full_response = str(response_data)
                                else:
                                    full_response = str(response_data)
                                
                                # Clean up the response
                                full_response = full_response.strip()
                                
                                # Update the placeholder with the full response
                                message_placeholder.write(full_response)
                                
                                # Add assistant response to chat history
                                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                                
                                # Force sidebar refresh for stats
                                st.experimental_rerun()
                            else:
                                full_response = "No output received from the model"
                            break
                        elif current_status == "FAILED":
                            full_response = f"Job failed: {status.get('error', 'Unknown error')}"
                            break
                        elif current_status == "CANCELLED":
                            full_response = "Job was cancelled"
                            break
                        
                        message_placeholder.write(f"Thinking... (Status: {current_status})")
                        time.sleep(2)
                
                # Update the placeholder with the full response
                message_placeholder.write(full_response)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                message_placeholder.write(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})
else:
    st.error("API key not found in .env file. Please create a .env file with your RUNPOD_API_KEY.") 