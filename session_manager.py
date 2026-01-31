# session_manager.py - CORRECTED VERSION
"""
Handles all session state management for the app.
Session state is Streamlit's way of persisting data between reruns.
Think of it as a dictionary that survives page refreshes.
"""

import streamlit as st
import time

def init_session_state():
    """
    Initialize all session state variables.
    This function should be called at the start of app.py
    """
    # Database connection state
    if 'db_path' not in st.session_state:
        st.session_state.db_path = None  # Path to current database file
    if 'connection' not in st.session_state:  # FIXED: was 'connecion'
        st.session_state.connection = None  # SQLite connection object
    if 'tables' not in st.session_state:
        st.session_state.tables = []  # List of table names
    
    # Query history state
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []  # List of past queries
    
    # UI state
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = None  # Currently selected table
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "explorer"  # Current active tab
    
    # User preferences
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {
            'rows_per_page': 100,
            'theme': 'light',
            'auto_run_queries': False
        }

def clear_database_state():
    """
    Clear all database-related session state.
    Called when user wants to load a new database or clear current one.
    """
    # Close existing connection if it exists
    if st.session_state.connection:
        try:
            st.session_state.connection.close()
        except:
            pass
    
    # Reset database state
    st.session_state.db_path = None
    st.session_state.connection = None
    st.session_state.tables = []
    st.session_state.selected_table = None

def add_to_query_history(query, success=True, rows_returned=0):
    """
    Add a query to the history with metadata.
    
    Args:
        query (str): The SQL query that was executed
        success (bool): Whether the query executed successfully
        rows_returned (int): Number of rows returned by the query
    """
    history_entry = {  # FIXED: was 'history_enry'
        'query': query,
        'timestamp': time.time(),
        'success': success,
        'rows_returned': rows_returned,
        'time': time.strftime("%H:%M:%S")
    }
    
    # Add to beginning of list (most recent first)
    st.session_state.query_history.insert(0, history_entry)
    
    # Keep only last 50 queries to prevent memory issues
    if len(st.session_state.query_history) > 50:
        st.session_state.query_history = st.session_state.query_history[:50]

def update_preference(key, value):
    """
    Update a user preference.
    
    Args:
        key (str): Preference key (e.g., 'rows_per_page')
        value: New value for the preference
    """
    if key in st.session_state.preferences:
        st.session_state.preferences[key] = value
        return True
    return False