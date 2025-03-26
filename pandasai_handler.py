# pandasai_handler.py
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
import streamlit as st
import matplotlib.pyplot as plt
import os
import glob
from datetime import datetime

# Get API key from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

llm = OpenAI(api_token=OPENAI_API_KEY)

# Define images folder and create it if it doesn't exist
IMG_DIR = "imgs"
os.makedirs(IMG_DIR, exist_ok=True)

def _rotate_old_charts(max_charts=30):
    """Delete older charts if the folder exceeds max_chart count."""
    files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")), key=os.path.getctime)
    while len(files) > max_charts:
        os.remove(files[0])
        files = files[1:]

def get_latest_chart(since_timestamp=None):
    """
    Get the latest saved chart file.
    
    Args:
        since_timestamp (float, optional): Only return charts created after this timestamp
        
    Returns:
        str or None: Path to the latest chart file, or None if no charts found or none meet the timestamp criteria
    """
    chart_files = glob.glob(os.path.join(IMG_DIR, "*.png"))
    if not chart_files:
        return None
        
    latest = max(chart_files, key=os.path.getctime)
    
    # If timestamp check is requested, verify the chart is newer than the timestamp
    if since_timestamp:
        created = os.path.getctime(latest)
        if created >= since_timestamp:
            return latest
        return None
    return latest

def initialize_smart_df(df):
    """
    Initialize a SmartDataframe with the provided pandas DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame to convert to SmartDataframe
        
    Returns:
        SmartDataframe: PandasAI SmartDataframe initialized with OpenAI LLM
    """
    return SmartDataframe(
        df, 
        config={
            "llm": llm,
            "save_charts": True,
            "save_charts_path": IMG_DIR,
            "verbose": True
        }
    )

def ask_pandasai(sdf, instruction):
    """
    Execute a PandasAI instruction on a SmartDataframe
    and return a path to a saved chart if one is generated.
    
    Args:
        sdf (SmartDataframe): SmartDataframe to query
        instruction (str): Instruction to execute
        
    Returns:
        dict: Response with type and content
    """
    try:
        # Capture current timestamp before running the query
        before_chat_time = datetime.now().timestamp()
        
        # Run PandasAI
        result = sdf.chat(instruction)
        print(f"[DEBUG] Result type: {type(result)} | Value: {result}")

        # Clean up older charts
        _rotate_old_charts()
        
        # Check for a chart created AFTER chat execution started
        latest_chart = get_latest_chart(since_timestamp=before_chat_time)

        if latest_chart:
            return {
                "type": "plot",
                "response": result,         # textual summary from PandasAI
                "filepath": latest_chart    # chart image path
            }
            
        # Handle non-chart results
        if isinstance(result, str):
            return {"type": "text", "response": result}
        elif hasattr(result, "to_dict"):  # likely a DataFrame
            return {"type": "dataframe", "response": result}
        else:
            return {"type": "text", "response": str(result)}

    except Exception as e:
        return {"type": "error", "response": str(e)}
