# modules/table_editor.py
"""
Module for editing table data (CRUD operations).
We'll keep this simple for now and expand later.
"""

import streamlit as st
import pandas as pd
from utils.database import execute_query, get_table_preview

def render_table_editor():
    """
    Render the table editor interface.
    """
    st.header("Table Editor")
    
    if not st.session_state.connection:
        st.info("Please upload a database file to edit tables.")
        return
    
    if not st.session_state.tables:
        st.info("No tables available for editing.")
        return
    
    # Table selection
    selected_table = st.selectbox(
        "Select table to edit:",
        st.session_state.tables,
        key="editor_table_select"
    )
    
    if not selected_table:
        return
    
    # CRUD operations tabs
    tab1, tab2, tab3 = st.tabs(["Insert Row", "Update Row", "Delete Row"])
    
    with tab1:
        render_insert_interface(selected_table)
    
    with tab2:
        render_update_interface(selected_table)
    
    with tab3:
        render_delete_interface(selected_table)

def render_insert_interface(table_name: str):
    """
    Render interface for inserting new rows.
    
    Args:
        table_name (str): Name of the table
    """
    st.subheader(f"Insert into {table_name}")
    
    # Get table schema to know columns
    try:
        schema_df = pd.read_sql_query(
            f"PRAGMA table_info({table_name})", 
            st.session_state.connection
        )
        
        if schema_df.empty:
            st.warning("Cannot get table schema.")
            return
        
        # Create form for inserting data
        with st.form(key=f"insert_form_{table_name}"):
            inputs = {}
            
            for _, row in schema_df.iterrows():
                col_name = row['name']
                col_type = row['type'].upper()
                
                # Skip primary key if it's auto-increment
                if 'PRIMARY KEY' in str(row['pk']) and 'AUTOINCREMENT' in col_type:
                    continue
                
                # Create appropriate input based on column type
                if 'INT' in col_type:
                    inputs[col_name] = st.number_input(col_name, step=1)
                elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
                    inputs[col_name] = st.number_input(col_name, step=0.01)
                elif 'TEXT' in col_type or 'CHAR' in col_type or 'VARCHAR' in col_type:
                    inputs[col_name] = st.text_input(col_name)
                else:
                    inputs[col_name] = st.text_input(col_name)
            
            # Submit button
            if st.form_submit_button("Insert Row", type="primary"):
                insert_row(table_name, inputs)
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

def insert_row(table_name: str, data: dict):
    """
    Insert a new row into the table.
    
    Args:
        table_name (str): Name of the table
        data (dict): Column-value pairs to insert
    """
    try:
        # Build INSERT query
        columns = ', '.join(data.keys())
        values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()])
        
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        
        # Execute query
        execute_query(st.session_state.connection, query)
        
        st.success("Row inserted successfully!")
        st.rerun()  # Refresh to show new data
        
    except Exception as e:
        st.error(f"Error inserting row: {str(e)}")

def render_update_interface(table_name: str):
    """
    Render interface for updating rows.
    Simple version - we'll implement fully later.
    """
    st.subheader(f"Update rows in {table_name}")
    st.info("Update functionality will be implemented in the next version.")
    
    # Show current data for reference
    try:
        df = get_table_preview(st.session_state.connection, table_name, limit=20)
        if not df.empty:
            st.write("**Current data (first 20 rows):**")
            st.dataframe(df, use_container_width=True)
    except:
        pass

def render_delete_interface(table_name: str):
    """
    Render interface for deleting rows.
    Simple version - we'll implement fully later.
    """
    st.subheader(f"Delete rows from {table_name}")
    st.info("Delete functionality will be implemented in the next version.")
    
    # Show warning about delete operations
    st.warning("""
     **Important:** 
    - DELETE operations are permanent
    - Always backup your database before deleting data
    - Consider using soft deletes (is_deleted flag) instead
    """)

# Note: We'll fully implement update and delete in a future version