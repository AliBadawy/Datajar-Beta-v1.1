from supabase import create_client, Client
import pandas as pd
import streamlit as st
import os
import toml

# Function to get credentials that works both in Streamlit and standalone mode
def get_supabase_credentials():
    # Try to get credentials from Streamlit secrets
    try:
        return st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    except (KeyError, RuntimeError):
        # Fallback for direct script execution: read from secrets.toml directly
        try:
            # Path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            secrets_path = os.path.join(base_dir, '.streamlit', 'secrets.toml')
            
            if os.path.exists(secrets_path):
                secrets = toml.load(secrets_path)
                return secrets.get("SUPABASE_URL"), secrets.get("SUPABASE_KEY")
            else:
                # Fallback test credentials for development
                print("Warning: Using default test credentials - not for production use")
                return "https://pdmwsbdhqcxlltghsbwr.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBkbXdzYmRocWN4bGx0Z2hzYndyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyNTUyMTgsImV4cCI6MjA1NjgzMTIxOH0.9STFOXHre8rKUWXaBUC2y6g8eIM4WPmfW32b8cBOlnk"
        except Exception as e:
            print(f"Error getting Supabase credentials: {e}")
            return None, None

# Get credentials
SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()

def fetch_supabase_table(table_name: str = "products") -> pd.DataFrame:
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Missing Supabase credentials")
            return pd.DataFrame()
            
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table(table_name).select("*").execute()

        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"[Supabase] Error fetching table: {e}")
        return pd.DataFrame()

# This allows the script to be run directly for testing
if __name__ == "__main__":
    print(f"Testing connection to Supabase...")
    df = fetch_supabase_table("waitlist")
    print(f"Results: {len(df)} rows")
    if not df.empty:
        print(df.head())