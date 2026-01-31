# app.py
"""
Main application file for SQLite Browser.
This is the entry point that brings everything together.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from session_manager import init_session_state
from modules.file_uploader import render_file_uploader, render_database_info
from modules.db_explorer import render_database_explorer
from modules.sql_editor import render_sql_editor
from modules.table_editor import render_table_editor
from modules.exporter import render_exporter

def main():
    """
    Main function that sets up and runs the SQLite Browser app.
    """
    # Page configuration - MUST be first Streamlit command
    st.set_page_config(
        page_title="SQLite Browser",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # App title and description
    st.title("SQLite Browser")
    st.markdown("""
    A web-based SQLite database explorer. Upload a `.db` or `.sqlite` file to explore, 
    query, and export your data.
    """)
    
    # Sidebar - File upload and database info
    with st.sidebar:
        # Render file uploader in sidebar
        new_db_loaded = render_file_uploader()
        
        # If a new database was loaded, rerun to update everything
        if new_db_loaded:
            st.rerun()
        
        # Show current database info if one is loaded
        render_database_info()
        
        # Add app info
        st.sidebar.divider()
        st.sidebar.info("""
        **Tips:**
        - Click column headers to sort
        - Use LIMIT for large tables
        - Your original file is not modified
        """)
    
    # Main content area - Tabs for different functionalities
    if st.session_state.connection:
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Explorer", 
            "SQL Editor", 
            "Editor", 
            "Export",
            "Settings"
        ])
        
        with tab1:
            # Database Explorer Tab
            render_database_explorer()
        
        with tab2:
            # SQL Editor Tab
            render_sql_editor()
        
        with tab3:
            # Table Editor Tab
            render_table_editor()
        
        with tab4:
            # Exporter Tab
            render_exporter()
        
        with tab5:
            # Settings Tab
            render_settings()
    
    else:
        # If no database is loaded, show welcome/instructions
        render_welcome_screen()

def render_settings():
    """
    Render the settings tab.
    """
    st.header("Settings")
    
    # Rows per page setting
    rows_per_page = st.slider(
        "Rows per page in preview:",
        min_value=10,
        max_value=500,
        value=st.session_state.preferences['rows_per_page'],
        step=10
    )
    
    if rows_per_page != st.session_state.preferences['rows_per_page']:
        from session_manager import update_preference
        update_preference('rows_per_page', rows_per_page)
        st.success("Settings updated!")
    
    # Clear history button
    st.subheader("Data Management")
    if st.button("Clear Query History", type="secondary"):
        st.session_state.query_history = []
        st.success("Query history cleared!")
    
    # App info
    st.divider()
    st.subheader("About")
    st.write("""
    **SQLite Browser** v1.0
    - Built with Streamlit
    - Uses Python's sqlite3 library
    - Data stays in your browser (no server storage)
    """)

def render_welcome_screen():
    """
    Render the welcome screen when no database is loaded.
    """
    st.header("Welcome to SQLite Browser!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Get Started")
        st.write("""
        1. **Upload a database** using the file uploader in the sidebar
        2. **Explore tables** in the Explorer tab
        3. **Run SQL queries** in the SQL Editor tab
        4. **Export data** in CSV, JSON, or Excel format
        """)
        
        st.info("Use the sidebar to upload your first database file")
    
    with col2:
        st.subheader("Supported Features")
        st.write("""
         **Database Exploration:**
        - View all tables
        - Preview table data
        - See table schemas
        
         **SQL Operations:**
        - Execute any SQL query
        - Query history
        - Example queries
        
         **Data Export:**
        - Export tables
        - Export query results
        - Download entire database
        
         **Basic Editing:**
        - Insert new rows
        - More coming soon!
        """)
    
    # Sample database creator
    with st.expander("🧪 Create a Sample Database for Testing"):
        if st.button("Create Sample Database"):
            create_sample_database()

def create_sample_database():
    """
    Create a sample database for testing.
    """
    import sqlite3
    import tempfile
    
    try:
        # Create a temporary database
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_path = tmp_file.name
        
        # Create sample database
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()
        
        # Create sample tables
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            category TEXT,
            in_stock INTEGER DEFAULT 0
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        ''')
        
        # Insert sample data
        cursor.execute("INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com')")
        cursor.execute("INSERT INTO users (username, email) VALUES ('bob', 'bob@example.com')")
        
        cursor.execute("INSERT INTO products VALUES (1, 'Laptop', 999.99, 'Electronics', 10)")
        cursor.execute("INSERT INTO products VALUES (2, 'Book', 19.99, 'Education', 50)")
        
        cursor.execute("INSERT INTO orders (user_id, product_id, quantity, order_date) VALUES (1, 1, 1, '2024-01-15')")
        cursor.execute("INSERT INTO orders (user_id, product_id, quantity, order_date) VALUES (2, 2, 3, '2024-01-16')")
        
        conn.commit()
        conn.close()
        
        # Load this database into the app
        with open(tmp_path, 'rb') as f:
            # Simulate file upload
            import io
            from modules.file_uploader import handle_uploaded_file
            
            class MockUploadedFile:
                def __init__(self, path):
                    with open(path, 'rb') as file:
                        self.value = file.read()
                
                def getvalue(self):
                    return self.value
            
            mock_file = MockUploadedFile(tmp_path)
            handle_uploaded_file(mock_file)
        
        st.success("Sample database created and loaded!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error creating sample database: {str(e)}")

if __name__ == "__main__":
    main()