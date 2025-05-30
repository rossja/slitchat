import json
import subprocess
import streamlit as st
import requests
from typing import List, Dict, Optional, Tuple

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"

# App title
st.set_page_config(
    page_title="SlitChat - Ollama Chat Interface",
    page_icon="💬",
    layout="wide",
)

def get_ollama_models() -> List[str]:
    """Fetch available models from Ollama using CLI command"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        lines = result.stdout.strip().split('\n')
        # Skip header line
        models = []
        for line in lines[1:]:
            if line.strip():
                # First word in each line is the model name
                models.append(line.split()[0])
        return models
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        return []

def send_message(model: str, messages: List[Dict], system_prompt: Optional[str] = None, stream: bool = True) -> Tuple[str, bool]:
    """Send message to Ollama API and return response"""
    url = f"{OLLAMA_BASE_URL}/api/chat"
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    
    # Add system prompt if provided
    if system_prompt:
        payload["system"] = system_prompt
    
    if stream:
        response_text = ""
        is_error = False
        
        try:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                content = chunk["message"]["content"]
                                response_text += content
                                yield response_text, False
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield str(e), True
    else:
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"], False
            else:
                return "Unexpected response format", True
        except Exception as e:
            return str(e), True

def main():
    # App header
    st.title("SlitChat - Chat with Ollama Models")
    
    # Initialize session state for chat history and selected model
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = ""
    
    # Sidebar for model selection
    with st.sidebar:
        st.header("Model Selection")
        
        # Fetch available models
        available_models = get_ollama_models()
        
        if available_models:
            selected_model = st.selectbox(
                "Choose a model",
                options=available_models,
                index=0 if st.session_state.selected_model is None else available_models.index(st.session_state.selected_model),
                key="model_selectbox"
            )
            
            # Update selected model in session state
            st.session_state.selected_model = selected_model
            
            # System prompt input
            st.header("System Prompt")
            system_prompt = st.text_area(
                "Customize the system prompt (optional)",
                value=st.session_state.system_prompt,
                placeholder="Enable deep thinking subroutine.",
                help="Provide specific instructions to guide the model's behavior",
                key="system_prompt_input"
            )
            
            # Update system prompt in session state
            st.session_state.system_prompt = system_prompt
            
            # Command syntax example
            st.markdown(
                """
                **Command Example:**
                ```
                /set system \"\"\"Your system prompt here\"\"\"
                ```
                """
            )
            
            # Reset chat button
            if st.button("Reset Chat"):
                st.session_state.messages = []
                st.rerun()
        else:
            st.error("No models available. Make sure Ollama is running.")
            st.session_state.selected_model = None
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if st.session_state.selected_model:
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Check for system prompt command
            if user_input.startswith("/set system"):
                try:
                    # Extract the system prompt from the command
                    # Format: /set system """prompt text"""
                    prompt_start = user_input.find('"""', 12)
                    if prompt_start != -1:
                        prompt_end = user_input.find('"""', prompt_start + 3)
                        if prompt_end != -1:
                            new_system_prompt = user_input[prompt_start + 3:prompt_end]
                            st.session_state.system_prompt = new_system_prompt
                            
                            # Add system message to chat
                            with st.chat_message("system"):
                                st.markdown(f"System prompt updated to: *{new_system_prompt}*")
                            
                            # No need to add this to the actual message history
                            st.rerun()
                        else:
                            st.error("Invalid system prompt format. Use: /set system \"\"\"Your prompt here\"\"\"")
                    else:
                        st.error("Invalid system prompt format. Use: /set system \"\"\"Your prompt here\"\"\"")
                except Exception as e:
                    st.error(f"Error setting system prompt: {str(e)}")
            else:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # Display assistant response with streaming
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    
                    # Prepare messages for API
                    api_messages = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in st.session_state.messages
                    ]
                    
                    # Stream the response
                    full_response = ""
                    for response_chunk, is_error in send_message(
                        st.session_state.selected_model, 
                        api_messages,
                        st.session_state.system_prompt if st.session_state.system_prompt else None,
                        stream=True
                    ):
                        if is_error:
                            st.error(response_chunk)
                            break
                        else:
                            full_response = response_chunk
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Final update without cursor
                    if not is_error:
                        message_placeholder.markdown(full_response)
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.info("Please select a model from the sidebar to start chatting.")

if __name__ == "__main__":
    main() 