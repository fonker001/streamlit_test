# modules/sql_editor.py
"""
Module for SQL query editing and execution.
"""

import streamlit as st
import pandas as pd
from utils.database import execute_query
from session_manager import add_to_query_history

def render_sql_editor():
    """
    Render the SQL query editor interface.
    """
    st.header("SQL Editor")
    
    if not st.session_state.connection:
        st.info("Please upload a database file to use the SQL editor.")
        return
    
    # Create two columns: left for editor, right for history
    col_editor, col_history = st.columns([2, 1])
    
    with col_editor:
        render_query_input()
    
    with col_history:
        render_query_history()

def render_query_input():
    """
    Render the SQL query input area and execute button.
    """
    # Text area for SQL input
    sql_query = st.text_area(
        "Enter SQL Query:",
        height=150,
        placeholder="SELECT * FROM users LIMIT 10;",
        help="Write your SQL query here. You can use SELECT, INSERT, UPDATE, DELETE, etc.",
        key="sql_text_area"
    )
    
    # Query execution controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Run Query", type="primary", use_container_width=True):
            execute_sql_query(sql_query)
    
    with col2:
        if st.button("Clear", use_container_width=True):
            # Clear the text area by rerunning
            st.rerun()
    
    with col3:
        with st.expander("Examples"):
            render_example_queries()

def execute_sql_query(query: str):
    """
    Execute a SQL query and display results.
    
    Args:
        query (str): SQL query to execute
    """
    if not query.strip():
        st.warning("Please enter a SQL query first.")
        return
    
    try:
        # Execute the query
        result_df = execute_query(st.session_state.connection, query)
        
        # Add to history
        rows_returned = len(result_df) if hasattr(result_df, '__len__') else 0
        add_to_query_history(query, success=True, rows_returned=rows_returned)
        
        # Display success message
        st.success("Query executed successfully!")
        
        # Display results if it's a SELECT query
        if query.strip().upper().startswith('SELECT'):
            if not result_df.empty:
                st.write(f"**Results ({len(result_df)} rows):**")
                st.dataframe(result_df, use_container_width=True)
            else:
                st.info("Query returned 0 rows.")
        else:
            # For non-SELECT queries, show the message
            st.info(result_df.iloc[0, 0] if not result_df.empty else "Query executed.")
            
    except Exception as e:
        # Add failed query to history
        add_to_query_history(query, success=False, rows_returned=0)
        st.error(f"Query Error: {str(e)}")

def render_query_history():
    """
    Render the query history panel.
    """
    st.subheader("Query History")
    
    if not st.session_state.query_history:
        st.info("No query history yet.")
        return
    
    # Display recent queries (most recent first)
    for i, entry in enumerate(st.session_state.query_history[:10]):  # Show last 10
        with st.expander(f"Query {i+1} - {entry['time']}"):
            # Color code based on success
            if entry['success']:
                st.success("Success")
                if entry['rows_returned'] > 0:
                    st.caption(f"Rows: {entry['rows_returned']}")
            else:
                st.error("Failed")
            
            # Show the query
            st.code(entry['query'], language="sql")
            
            # Re-run button
            if st.button(f"Re-run", key=f"rerun_{i}"):
                # Store query to text area (will be picked up on next run)
                st.session_state.sql_text_area = entry['query']
                st.rerun()

def render_example_queries():
    """
    Render example SQL queries.
    """
    examples = {
        "Basic Select": "SELECT * FROM users LIMIT 10;",
        "Count Rows": "SELECT COUNT(*) FROM products;",
        "Filter Data": "SELECT * FROM orders WHERE status = 'completed';",
        "Join Tables": """SELECT u.name, o.order_date, o.total
FROM users u
JOIN orders o ON u.id = o.user_id;""",
        "See Schema": "PRAGMA table_info(users);",
        "List Tables": "SELECT name FROM sqlite_master WHERE type='table';"
    }
    
    for title, query in examples.items():
        st.write(f"**{title}:**")
        st.code(query, language="sql")