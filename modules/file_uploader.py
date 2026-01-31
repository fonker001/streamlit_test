# modules/file_uploader.py
"""
Module for handling file uploads and database initialization.
"""

import streamlit as st
import tempfile
from utils.database import connect_to_database, get_table_list

def render_file_uploader():
    """
    Render the file uploader widget and handle file uploads.
    
    Returns:
        bool: True if a new database was loaded, False otherwise
    """
    st.header("Database Upload")
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "Upload SQLite Database",
        type=['db', 'sqlite', 'sqlite3'],
        help="Upload a .db, .sqlite, or .sqlite3 file"
    )
    
    if uploaded_file is not None:
        return handle_uploaded_file(uploaded_file)
    
    return False

def handle_uploaded_file(uploaded_file):
    """
    Process an uploaded database file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        bool: True if database was loaded successfully
    """
    try:
        # Create temporary file to store the uploaded database
        # We need a physical file because SQLite requires file system access
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Check if this is a new database (different from current)
        if st.session_state.db_path != tmp_path:
            # Import session manager to clear old state
            from session_manager import clear_database_state
            
            # Clear existing database state
            clear_database_state()
            
            # Connect to new database
            conn = connect_to_database(tmp_path)
            
            # Update session state
            st.session_state.connection = conn
            st.session_state.db_path = tmp_path
            st.session_state.tables = get_table_list(conn)
            
            st.success(f"Database loaded successfully! Found {len(st.session_state.tables)} tables.")
            return True
            
    except Exception as e:
        st.error(f"Error loading database: {str(e)}")
        return False
    
    return False

def render_database_info():
    """
    Display current database information in the sidebar.
    """
    if st.session_state.connection:
        st.sidebar.subheader("Current Database")
        
        # Show file name (extract from path)
        if st.session_state.db_path:
            filename = st.session_state.db_path.split('/')[-1]
            st.sidebar.write(f"**File:** `{filename}`")
        
        # Show table count
        st.sidebar.metric("Tables", len(st.session_state.tables))
        
        # Clear database button
        if st.sidebar.button("Clear Database", type="secondary"):
            from session_manager import clear_database_state
            clear_database_state()
            st.rerun()
        
        st.sidebar.divider()