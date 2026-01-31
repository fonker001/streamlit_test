# modules/db_explorer.py
"""
Module for exploring database structure and viewing table data.
"""

import streamlit as st
import pandas as pd
from utils.database import get_table_preview, get_table_schema

def render_database_explorer():
    """
    Main function to render the database explorer tab.
    """
    st.header("Database Explorer")
    
    if not st.session_state.connection:
        st.info("Please upload a database file to start exploring.")
        return
    
    # Create two columns: left for table list, right for table details
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        render_table_list()
    
    with col_right:
        if st.session_state.selected_table:
            render_table_details()

def render_table_list():
    """
    Render the list of tables in the database.
    """
    st.subheader("Tables")
    
    if not st.session_state.tables:
        st.info("No tables found in the database.")
        return
    
    # Create a selectbox for table selection
    selected_table = st.selectbox(
        "Select a table:",
        st.session_state.tables,
        key="table_selectbox"
    )
    
    # Update session state if selection changed
    if selected_table != st.session_state.selected_table:
        st.session_state.selected_table = selected_table
        # No need to rerun - Streamlit will handle the update
    
    # Display table list with counts
    st.write("**All tables:**")
    for table in st.session_state.tables:
        # Highlight selected table
        if table == st.session_state.selected_table:
            st.write(f"**{table}**")
        else:
            st.write(f"• {table}")

def render_table_details():
    """
    Render details for the selected table.
    """
    if not st.session_state.selected_table:
        return
    
    table_name = st.session_state.selected_table
    
    # Create tabs for different views of the table
    tab1, tab2, tab3 = st.tabs(["Data Preview", "🔧 Schema", "📈 Statistics"])
    
    with tab1:
        render_data_preview(table_name)
    
    with tab2:
        render_table_schema(table_name)
    
    with tab3:
        render_table_statistics(table_name)

def render_data_preview(table_name: str):
    """
    Render a preview of table data.
    
    Args:
        table_name (str): Name of the table to preview
    """
    st.subheader(f"Data: {table_name}")
    
    try:
        # Get data preview
        df = get_table_preview(
            st.session_state.connection, 
            table_name, 
            limit=st.session_state.preferences['rows_per_page']
        )
        
        # Display row count info
        total_rows = len(df)
        st.write(f"Showing first **{total_rows}** rows")
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading table data: {str(e)}")

def render_table_schema(table_name: str):
    """
    Render table schema information.
    
    Args:
        table_name (str): Name of the table
    """
    st.subheader(f"Schema: {table_name}")
    
    try:
        # Get schema information
        schema_df = get_table_schema(st.session_state.connection, table_name)
        
        if schema_df.empty:
            st.info(f"No schema information available for table '{table_name}'")
            return
        
        # Display schema in a nice format
        st.dataframe(schema_df, use_container_width=True)
        
        # Show CREATE TABLE statement in expander
        with st.expander("View CREATE TABLE Statement"):
            try:
                create_query = f"SELECT sql FROM sqlite_master WHERE name='{table_name}'"
                create_stmt = pd.read_sql_query(create_query, st.session_state.connection)
                
                if not create_stmt.empty and create_stmt.iloc[0, 0]:
                    st.code(create_stmt.iloc[0, 0], language="sql")
                else:
                    st.info("CREATE TABLE statement not available")
            except:
                st.info("CREATE TABLE statement not available")
                
    except Exception as e:
        st.error(f"Error loading schema: {str(e)}")

def render_table_statistics(table_name: str):
    """
    Render basic statistics for the table.
    
    Args:
        table_name (str): Name of the table
    """
    st.subheader(f"Statistics: {table_name}")
    
    try:
        # Get basic stats
        query = f"SELECT COUNT(*) as row_count FROM {table_name}"
        count_df = pd.read_sql_query(query, st.session_state.connection)
        
        # Create metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Rows", count_df.iloc[0, 0])
        
        with col2:
            # Try to get column count
            schema_df = get_table_schema(st.session_state.connection, table_name)
            st.metric("Columns", len(schema_df))
        
        # Show data types distribution
        st.write("**Column Types:**")
        if not schema_df.empty:
            type_counts = schema_df['type'].value_counts()
            st.bar_chart(type_counts)
        
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")