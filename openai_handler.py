import openai
import json
import streamlit as st

# Get API key from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize the OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_openai_response(messages, df=None):
    """
    Send messages to OpenAI API and get a response
    
    Args:
        messages (list): List of message dictionaries with role and content
        df (pandas.DataFrame, optional): DataFrame to analyze and include in context
        
    Returns:
        str: Response content from OpenAI
    """
    # Check if API key exists
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        st.error("OpenAI API key not found. Please set your API key in .streamlit/secrets.toml")
        return "Error: OpenAI API key not found. Please set your API key in .streamlit/secrets.toml"
    
    # If DataFrame is provided, add marketing expert system message with CSV analysis
    if df is not None:
        df_metadata = analyze_dataframe(df)
        system_message = {
            "role": "system",
            "content": f"""You are a senior **marketing data expert** helping a client explore and analyze their advertising and campaign dataset.

The user has uploaded a dataset. Your job is to:
- Understand its structure
- Identify patterns or insights
- Assist with interpreting performance metrics
- Provide clear, actionable answers based on the context

Here's what we know about the data:
{json.dumps(df_metadata, indent=2)}

You should:
- Be specific when referencing column names, categories, or missing data
- Highlight any interesting trends or anomalies if asked
- Provide explanations in simple, business-friendly language
- Visualize when possible (bar charts, comparisons, summaries)

Your responses should guide the user in making **data-driven marketing decisions**.
"""
        }
        # Prepend system message to the messages list
        messages = [system_message] + messages
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

def get_streaming_response(messages, df=None):
    """
    Send messages to OpenAI API and get a streaming response
    
    Args:
        messages (list): List of message dictionaries with role and content
        df (pandas.DataFrame, optional): DataFrame to analyze and include in context
        
    Returns:
        generator: Yields response content chunks from OpenAI
    """
    # Check if API key exists
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        yield "Error: OpenAI API key not found. Please set your API key in .streamlit/secrets.toml"
        return
    
    # If DataFrame is provided, add marketing expert system message with CSV analysis
    if df is not None:
        df_metadata = analyze_dataframe(df)
        system_message = {
            "role": "system",
            "content": f"""You are a senior **marketing data expert** helping a client explore and analyze their advertising and campaign dataset.

The user has uploaded a dataset. Your job is to:
- Understand its structure
- Identify patterns or insights
- Assist with interpreting performance metrics
- Provide clear, actionable answers based on the context

Here's what we know about the data:
{json.dumps(df_metadata, indent=2)}

You should:
- Be specific when referencing column names, categories, or missing data
- Highlight any interesting trends or anomalies if asked
- Provide explanations in simple, business-friendly language
- Visualize when possible (bar charts, comparisons, summaries)

Your responses should guide the user in making **data-driven marketing decisions**.
"""
        }
        # Prepend system message to the messages list
        messages = [system_message] + messages
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True
        )
        
        # Process the streaming response
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    yield chunk_message
                
    except Exception as e:
        yield f"Sorry, I encountered an error: {str(e)}"

def analyze_dataframe(df):
    """
    Analyze a pandas DataFrame and extract metadata for GPT context
    
    Args:
        df (pandas.DataFrame): DataFrame to analyze
        
    Returns:
        dict: Dictionary containing metadata about the DataFrame
    """
    analysis = {}

    # 1. Head rows
    analysis["head_rows"] = df.head(5).to_dict(orient="records")

    # 2. Data types
    analysis["data_types"] = df.dtypes.astype(str).to_dict()

    # 3. Shape
    analysis["shape"] = {"rows": df.shape[0], "columns": df.shape[1]}

    # 4. Missing data
    missing = df.isnull().sum()
    missing_data = {}
    for col, count in missing.items():
        if count > 0:
            missing_data[col] = {
                "missing_count": int(count),
                "missing_percent": round((count / len(df)) * 100, 2)
            }
    analysis["missing_data"] = missing_data

    # 5. Categorical columns
    categorical_data = {}
    for col in df.select_dtypes(include=["object", "category"]).columns:
        value_counts = df[col].value_counts(normalize=True).head(5)
        categorical_data[col] = {
            "unique_values": list(value_counts.index),
            "distribution": {k: round(v, 4) for k, v in value_counts.items()}
        }
    analysis["categorical_data"] = categorical_data

    return analysis

def classify_user_prompt(prompt, df=None):
    """
    Use GPT to determine whether the prompt is a conversational or data analysis request.
    Optionally include dataset metadata for more accurate classification.
    
    Args:
        prompt (str): The user's message to classify
        df (pandas.DataFrame, optional): DataFrame to provide context
        
    Returns:
        str: 'chat' or 'data_analysis'
    """
    dataset_info = json.dumps(analyze_dataframe(df), indent=2) if df is not None else "No dataset provided."

    system_msg = {
        "role": "system",
        "content": (
            "You are a smart classification assistant.\n"
            "Your job is to classify the user's intent based on their message and the dataset they have uploaded.\n\n"
            "Label the message as:\n"
            "- 'chat': if it's a general question, explanation, or non-analytical request.\n"
            "- 'data_analysis': if it's asking to compare, analyze, filter, calculate, summarize, visualize, or explore dataset columns, or any question related to the uploaded dataset.\n\n"
            "Only reply with: 'chat' or 'data_analysis'.\n\n"
            "Here is the dataset metadata to help you decide:\n"
            f"{dataset_info}"
        )
    }

    user_msg = {"role": "user", "content": prompt}

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_msg, user_msg]
        )
        result = response.choices[0].message.content.strip().lower()
        return result if result in ["chat", "data_analysis"] else "didn't understand"
    except Exception:
        return "error happened"  # fallback

def generate_pandasai_instruction(user_question, df):
    """
    Generate a short, direct instruction for PandasAI based on user question and dataset structure.
    
    Args:
        user_question (str): The user's original question about the data
        df (pandas.DataFrame): The DataFrame being analyzed
        
    Returns:
        str: A concise instruction formatted for PandasAI
    """
    df_metadata = analyze_dataframe(df)

    system_prompt = {
        "role": "system",
        "content": f"""You are a marketing data expert assistant.
You will be given a question about a dataset. Your job is to rewrite it into a clear, concise instruction for a pandas-based agent (PandasAI).

Dataset info:
{json.dumps(df_metadata, indent=2)}

Examples:
Q: What was the best performing campaign in terms of ROAS?
→ Instruction: Show the campaign with the highest ROAS.

Q: How many regions had above average CTR?
→ Instruction: Count the number of regions where CTR is above average.
"""
    }

    messages = [
        system_prompt,
        {"role": "user", "content": user_question}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating PandasAI prompt: {str(e)}"
