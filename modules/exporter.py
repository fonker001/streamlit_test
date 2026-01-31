# modules/exporter.py
"""
Module for exporting data from the database.
"""

import streamlit as st
import pandas as pd
import os
from utils.database import execute_query

def render_exporter():
    """
    Render the data exporter interface.
    """
    st.header("Export Data")
    
    if not st.session_state.connection:
        st.info("Please upload a database file to export data.")
        return
    
    # Export options tabs
    tab1, tab2, tab3 = st.tabs(["Export Table", "💾 Export Query Results", "🗂️ Export Entire DB"])
    
    with tab1:
        render_table_export()
    
    with tab2:
        render_query_export()
    
    with tab3:
        render_database_export()

def render_table_export():
    """
    Render interface for exporting entire tables.
    """
    st.subheader("Export Table")
    
    if not st.session_state.tables:
        st.info("No tables available for export.")
        return
    
    # Table selection
    table_name = st.selectbox(
        "Select table to export:",
        st.session_state.tables,
        key="export_table_select"
    )
    
    if not table_name:
        return
    
    # Format selection
    export_format = st.radio(
        "Export format:",
        ["CSV", "JSON", "Excel"],
        horizontal=True
    )
    
    # Export button
    if st.button("Export Table", type="primary"):
        export_table_data(table_name, export_format)

def export_table_data(table_name: str, format: str):
    """
    Export table data in specified format.
    
    Args:
        table_name (str): Name of the table to export
        format (str): Export format (CSV, JSON, Excel)
    """
    try:
        # Get all data from table
        query = f"SELECT * FROM {table_name}"
        df = execute_query(st.session_state.connection, query)
        
        if df.empty:
            st.warning("Table is empty.")
            return
        
        # Convert to requested format
        if format == "CSV":
            data = df.to_csv(index=False)
            mime_type = "text/csv"
            file_extension = "csv"
        elif format == "JSON":
            data = df.to_json(orient="records", indent=2)
            mime_type = "application/json"
            file_extension = "json"
        elif format == "Excel":
            data = df.to_excel(index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_extension = "xlsx"
        else:
            st.error("Unsupported format")
            return
        
        # Create download button
        st.download_button(
            label=f"Download {table_name}.{file_extension}",
            data=data,
            file_name=f"{table_name}.{file_extension}",
            mime=mime_type
        )
        
        # Show preview
        st.success(f"Ready to export {len(df)} rows from '{table_name}'")
        with st.expander("Preview data"):
            st.dataframe(df.head(10), use_container_width=True)
            
    except Exception as e:
        st.error(f"Export error: {str(e)}")

def render_query_export():
    """
    Render interface for exporting query results.
    """
    st.subheader("Export Query Results")
    
    # Query input
    query = st.text_area(
        "Enter SQL query:",
        height=100,
        placeholder="SELECT * FROM users WHERE status = 'active';",
        key="export_query"
    )
    
    # Format selection
    export_format = st.radio(
        "Export format:",
        ["CSV", "JSON", "Excel"],
        horizontal=True,
        key="query_export_format"
    )
    
    # Export button
    if st.button("Export Query Results", type="primary"):
        if not query.strip():
            st.warning("Please enter a SQL query.")
            return
        
        export_query_results(query, export_format)

def export_query_results(query: str, format: str):
    """
    Export query results in specified format.
    
    Args:
        query (str): SQL query to execute
        format (str): Export format
    """
    try:
        # Execute query
        df = execute_query(st.session_state.connection, query)
        
        if df.empty:
            st.warning("Query returned no results.")
            return
        
        # Convert to requested format
        if format == "CSV":
            data = df.to_csv(index=False)
            mime_type = "text/csv"
            file_extension = "csv"
        elif format == "JSON":
            data = df.to_json(orient="records", indent=2)
            mime_type = "application/json"
            file_extension = "json"
        elif format == "Excel":
            data = df.to_excel(index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_extension = "xlsx"
        else:
            st.error("Unsupported format")
            return
        
        # Create download button
        st.download_button(
            label=f"Download query_results.{file_extension}",
            data=data,
            file_name=f"query_results.{file_extension}",
            mime=mime_type
        )
        
        # Show preview
        st.success(f"Ready to export {len(df)} rows")
        with st.expander("Preview results"):
            st.dataframe(df.head(10), use_container_width=True)
            
    except Exception as e:
        st.error(f"Export error: {str(e)}")

def render_database_export():
    """
    Render interface for exporting the entire database.
    """
    st.subheader("Export Entire Database")
    
    if not st.session_state.db_path or not os.path.exists(st.session_state.db_path):
        st.info("No database file available for export.")
        return
    
    st.write("Download the entire SQLite database file:")
    
    # Read database file
    try:
        with open(st.session_state.db_path, 'rb') as f:
            db_data = f.read()
        
        # Get filename
        filename = os.path.basename(st.session_state.db_path)
        if not filename.endswith('.db'):
            filename = "database.db"
        
        # Download button
        st.download_button(
            label="Download Database File",
            data=db_data,
            file_name=filename,
            mime="application/x-sqlite3"
        )
        
        # Show database info
        st.info(f"""
        **Database Information:**
        - File size: {len(db_data) / 1024:.1f} KB
        - Tables: {len(st.session_state.tables)}
        - This will download the exact database file you uploaded
        """)
        
    except Exception as e:
        st.error(f"Error reading database file: {str(e)}")