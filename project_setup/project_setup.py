import streamlit as st
import os
import pandas as pd
from pandasai_handler import initialize_smart_df

def load_project_setup():
    # Load styling
    css_path = os.path.join(os.path.dirname(__file__), "project_setup_style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Add a container with a specific class to scope our CSS
    st.markdown('<div class="project-setup-container">', unsafe_allow_html=True)
    
    st.title("📁 Project Setup")
    st.markdown("Connect a data source or upload CSV files to begin analysis.")
    
    # Initialize csv_files in session state if it doesn't exist
    if "csv_files" not in st.session_state:
        st.session_state["csv_files"] = []

    # Row 1: Facebook Connect and Supabase Connect cards
    col1, col2 = st.columns([1, 1])
    
    # Facebook Connect Card
    with col1:
        st.markdown("### 📘 Connect with Facebook")
        facebook_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "facebook_logo.svg")
        st.image(facebook_logo_path, width=48)
        
        if st.button("Connect", key="facebook_connect"):
            try:
                # Check if the Facebook sample is already in the list
                if not any(f["name"] == "facebook_page_sample.csv" for f in st.session_state["csv_files"]):
                    # Path to Facebook sample data
                    facebook_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                               "FacebookConnect", "facebook_page_sample.csv")
                    # Load the data
                    df = pd.read_csv(facebook_path)
                    # Add to our list of CSV files
                    st.session_state["csv_files"].append({
                        "name": "facebook_page_sample.csv",
                        "df": df
                    })
                    
                    # Set as active DataFrame if it's our first file
                    if len(st.session_state["csv_files"]) == 1:
                        st.session_state["df"] = df
                        st.session_state["sdf"] = initialize_smart_df(df)
                        st.session_state["csv_filename"] = "facebook_page_sample.csv"
                    
                    st.success("✅ Facebook Page data loaded.")
                else:
                    st.info("📘 Facebook Page data is already loaded.")
            except Exception as e:
                st.error(f"❌ Could not load Facebook data: {e}")
    
    # Supabase Connect Card
    with col2:
        st.markdown("### 📡 Connect with Supabase")
        supabase_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "supabase_logo.png")
        st.image(supabase_logo_path, width=48)
        
        if st.button("Connect", key="supabase_connect"):
            try:
                # Check if Supabase data is already loaded
                if not any(f["name"] == "supabase_data.csv" for f in st.session_state["csv_files"]):
                    # Import the Supabase fetch module
                    from SupabaseConnect.supabase_fetch import fetch_supabase_table
                    
                    # Fetch data from Supabase
                    df = fetch_supabase_table("waitlist")
                    
                    if not df.empty:
                        # Add to our list of CSV files
                        st.session_state["csv_files"].append({
                            "name": "supabase_data.csv",
                            "df": df
                        })
                        
                        # Set as active DataFrame if it's our first file
                        if len(st.session_state["csv_files"]) == 1:
                            st.session_state["df"] = df
                            st.session_state["sdf"] = initialize_smart_df(df)
                            st.session_state["csv_filename"] = "supabase_data.csv"
                        
                        st.success("✅ Supabase data loaded.")
                    else:
                        st.warning("⚠️ No data returned from Supabase.")
                else:
                    st.info("📡 Supabase data is already loaded.")
            except Exception as e:
                st.error(f"❌ Failed to fetch from Supabase: {e}")
    
    # Row 2: CSV Upload Card
    st.markdown("---")
    st.markdown("### 📄 Upload CSV Files")
    
    col_csv, _ = st.columns([1, 1])
    with col_csv:
        csv_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "csv_icon.svg")
        st.image(csv_icon_path, width=48)
        
        # File uploader for multiple CSV files
        uploaded_files = st.file_uploader(
            "Choose CSV files",
            type=["csv"],
            accept_multiple_files=True,
            key="project_multi_upload"
        )
        
        # Process any new uploads
        if uploaded_files:
            existing_names = [f["name"] for f in st.session_state["csv_files"]]
            for uploaded_file in uploaded_files:
                # Check if the file is already in the list (by name)
                if uploaded_file.name not in existing_names:
                    try:
                        df = pd.read_csv(uploaded_file)
                        # Add to our list of CSV files
                        st.session_state["csv_files"].append({
                            "name": uploaded_file.name,
                            "df": df
                        })
                        
                        # Set as active DataFrame if it's our first or only file
                        if len(st.session_state["csv_files"]) == 1:
                            st.session_state["df"] = df
                            st.session_state["sdf"] = initialize_smart_df(df)
                            st.session_state["csv_filename"] = uploaded_file.name
                            
                        st.success(f"✅ Uploaded: {uploaded_file.name}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to read {uploaded_file.name}: {e}")

    # Display uploaded files with card-style design
    if st.session_state["csv_files"]:
        st.markdown("---")
        st.markdown("### 📄 Uploaded Files:")
        
        # Create card-style containers for each file
        for i, file_entry in enumerate(st.session_state["csv_files"]):
            with st.container():
                # Add card styling with a light background
                st.markdown(f"""
                <div style="
                    background-color: rgba(240, 242, 246, 0.4); 
                    border-radius: 10px; 
                    padding: 15px; 
                    margin-bottom: 10px;
                    border: 1px solid rgba(230, 234, 241, 0.7);">
                </div>
                """, unsafe_allow_html=True)
                
                # Place content inside the card
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{file_entry['name']}**")
                    st.caption(f"{file_entry['df'].shape[0]} rows × {file_entry['df'].shape[1]} columns")
                
                # Set as active button
                with col2:
                    active = st.session_state.get("csv_filename") == file_entry["name"]
                    if active:
                        st.success("🔍 Active")
                    else:
                        if st.button("🔍 Set Active", key=f"active_{i}"):
                            st.session_state["df"] = file_entry["df"]
                            st.session_state["sdf"] = initialize_smart_df(file_entry["df"])
                            st.session_state["csv_filename"] = file_entry["name"]
                            st.rerun()
                    
                # Remove button
                with col3:
                    if st.button("❌ Remove", key=f"remove_{i}"):
                        # If removing the active file, update the active file
                        if st.session_state.get("csv_filename") == file_entry["name"]:
                            if len(st.session_state["csv_files"]) > 1:
                                # Set another file as active
                                next_index = 0 if i > 0 else 1
                                next_file = st.session_state["csv_files"][next_index]
                                st.session_state["df"] = next_file["df"]
                                st.session_state["sdf"] = initialize_smart_df(next_file["df"])
                                st.session_state["csv_filename"] = next_file["name"]
                            else:
                                # No more files, clear the active file
                                if "df" in st.session_state:
                                    del st.session_state["df"]
                                if "sdf" in st.session_state:
                                    del st.session_state["sdf"]
                                if "csv_filename" in st.session_state:
                                    del st.session_state["csv_filename"]
                        
                        # Remove the file from the list
                        del st.session_state["csv_files"][i]
                        st.rerun()
    
    # Add a button to return to chat
    st.markdown("---")
    if st.button("Return to Chat"):
        st.query_params = {"page": "chat"}
        st.rerun()
    
    # Close the container div
    st.markdown('</div>', unsafe_allow_html=True)
