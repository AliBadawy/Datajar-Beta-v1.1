import streamlit as st
import time
import os
from openai_handler import get_openai_response, get_streaming_response, generate_pandasai_instruction, classify_user_prompt
from pandasai_handler import initialize_smart_df, ask_pandasai
from project_setup.project_setup import load_project_setup

# Page configuration
st.set_page_config(
    page_title="DataJar Chat",
    page_icon="💬",
    layout="centered"
)

# Get query parameters for navigation
page = st.query_params.get("page", "chat")

# Function to load and apply CSS
def load_css():
    """Load and apply CSS from style.css file in a way that works in both local and hosted environments"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Create the path to the CSS file
        css_file = os.path.join(script_dir, "style.css")
        
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS: {e}")
        # Fallback minimal styling if the CSS file can't be loaded
        st.markdown("""
        <style>
        .stChatMessage {border-radius: 10px; padding: 10px;}
        .stChatMessage.user {background-color: #2f2f2f;}
        .stChatMessage.assistant {background-color: #333333;}
        </style>
        """, unsafe_allow_html=True)

# Apply CSS styling
load_css()

# Display API key information
st.sidebar.title("API Settings")
if not st.secrets.get("OPENAI_API_KEY"):
    st.sidebar.warning("⚠️ OpenAI API key not found")
    st.sidebar.info("To use this app, please update your API key in the secrets management.")
    st.sidebar.code("# In secrets management\nOPENAI_API_KEY = 'your-actual-api-key'")

# Simplified Sidebar
st.sidebar.markdown("---")
st.sidebar.header("📊 Data Source")

# Display CSV status
if "csv_filename" in st.session_state:
    st.sidebar.success(f"🟢 {st.session_state['csv_filename']}")
else:
    st.sidebar.warning("🔴 No CSV uploaded")

# Navigation button
if st.sidebar.button("📁 Project Setup"):
    st.query_params = {"page": "project-setup"}
    st.rerun()

# Footer information
st.sidebar.markdown("---")
st.sidebar.caption("DataJar Chat - Phase 1")
st.sidebar.caption("Powered by OpenAI API")

# Route to the appropriate page based on query parameters
if page == "project-setup":
    load_project_setup()
else:  # Default to chat
    st.title("💬 Chat with DataJar")

    # Initialize session state for messages if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How can I help you analyze your ads today?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Display chart if the message contains a chart path
            if message.get("chart_path"):
                st.image(message["chart_path"], use_column_width=True)

    # Stream response with a realistic typing effect
    def stream_response(text):
        """
        Generator function that yields words with a delay to create a typing effect
        """
        for word in text.split():
            yield word + " "
            time.sleep(0.04)  # Delay between words for realistic typing effect

    # Handle user input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 1. Get classification mode - is this a chat or data analysis question?
        mode = "chat"  # Default fallback
        if "df" in st.session_state:
            mode = classify_user_prompt(prompt, df=st.session_state.get("df"))
        
        # 2. Store mode for dev display
        st.session_state["mode"] = mode
        
        # Route the request based on classification
        if mode == "data_analysis" and "df" in st.session_state and "sdf" in st.session_state:
            # Generate PandasAI instruction using GPT
            with st.spinner("Analyzing your question..."):
                pandas_prompt = generate_pandasai_instruction(prompt, df=st.session_state["df"])
            
            # Execute via PandasAI
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Processing data..."):
                    pandas_result = ask_pandasai(st.session_state["sdf"], pandas_prompt)
                    
                    # Handle different result types
                    if pandas_result["type"] == "text":
                        message_placeholder.markdown(pandas_result["response"])
                        # Save assistant message
                        st.session_state.messages.append({"role": "assistant", "content": pandas_result["response"]})
                    elif pandas_result["type"] == "dataframe":
                        # Display the dataframe
                        message_placeholder.dataframe(pandas_result["response"])
                        # Also save a text description
                        result_text = f"Here's the requested data analysis result."
                        st.session_state.messages.append({"role": "assistant", "content": result_text})
                    elif pandas_result["type"] == "plot":
                        result_text = pandas_result["response"]
                        chart_path = pandas_result.get("filepath")

                        # Show PandasAI response
                        message_placeholder.markdown(result_text)

                        # Show chart if it exists
                        if chart_path and os.path.exists(chart_path):
                            message_placeholder.image(chart_path, caption="📊 Here's your chart", use_column_width=True)

                        # Save response to chat history
                        chat_message = {
                            "role": "assistant",
                            "content": result_text
                        }
                        if chart_path:
                            chat_message["chart_path"] = chart_path

                        st.session_state.messages.append(chat_message)
                    elif pandas_result["type"] == "error":
                        message_placeholder.error(pandas_result["response"])
                        # Save error message
                        st.session_state.messages.append({"role": "assistant", "content": f"Error: {pandas_result['response']}"})
                    
                    # Developer Expander to show debug information
                    with st.expander("🧠 Developer Debug Info"):
                        st.markdown(f"**Mode:** `{mode}`")
                        st.markdown("**PandasAI Instruction:**")
                        st.code(pandas_prompt, language="markdown")
        else:
            # Use regular OpenAI response for chat mode
            # Get and display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Use streaming API to get response chunks
                with st.spinner("Thinking..."):
                    # Pass DataFrame to the streaming response function if available
                    if "df" in st.session_state:
                        for response_chunk in get_streaming_response(st.session_state.messages, df=st.session_state["df"]):
                            full_response += response_chunk
                            message_placeholder.markdown(full_response + "▌")
                    else:
                        for response_chunk in get_streaming_response(st.session_state.messages):
                            full_response += response_chunk
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Replace the placeholder with the complete response
                    message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Developer Debug Info for chat mode
                with st.expander("🧠 Developer Debug Info"):
                    st.markdown(f"**Mode:** `{mode}`")
