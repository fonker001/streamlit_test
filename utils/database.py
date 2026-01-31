# utils/database.py
"""
Database utility functions for SQLite operations.
This module handles all direct database interactions.
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
import tempfile
import os

def connect_to_database(db_path: str) -> sqlite3.Connection:
    """
    Create a connection to a SQLite database.
    
    Args:
        db_path (str): Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    try:
        conn = sqlite3.connect(db_path)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def get_table_list(conn: sqlite3.Connection) -> List[str]:
    """
    Get list of all tables in the database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        
    Returns:
        List[str]: List of table names
    """
    try:
        query = """
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
        df = pd.read_sql_query(query, conn)
        return df['name'].tolist()
    except Exception as e:
        print(f"Error getting table list: {e}")
        return []

def get_table_schema(conn: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    """
    Get schema information for a specific table.
    
    Args:
        conn (sqlite3.Connection): Database connection
        table_name (str): Name of the table
        
    Returns:
        pd.DataFrame: Schema information including column names, types, etc.
    """
    try:
        query = f"PRAGMA table_info({table_name})"
        return pd.read_sql_query(query, conn)
    except Exception as e:
        raise Exception(f"Error getting schema for table '{table_name}': {str(e)}")

def execute_query(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as DataFrame.
    
    Args:
        conn (sqlite3.Connection): Database connection
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame: Query results
    """
    try:
        # Convert query to uppercase to check type
        query_upper = query.strip().upper()
        
        # For SELECT queries, use pandas
        if query_upper.startswith('SELECT'):
            return pd.read_sql_query(query, conn)
        
        # For other queries (INSERT, UPDATE, DELETE, CREATE, etc.)
        else:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            
            # For queries that return rowcount (INSERT, UPDATE, DELETE)
            if cursor.rowcount >= 0:
                return pd.DataFrame({
                    'message': [f'Query executed successfully. Rows affected: {cursor.rowcount}']
                })
            else:
                # For CREATE, DROP, etc.
                return pd.DataFrame({
                    'message': ['Query executed successfully.']
                })
            
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")

def get_table_preview(conn: sqlite3.Connection, table_name: str, limit: int = 100) -> pd.DataFrame:
    """
    Get a preview of table data.
    
    Args:
        conn (sqlite3.Connection): Database connection
        table_name (str): Name of the table
        limit (int): Number of rows to return
        
    Returns:
        pd.DataFrame: Table data preview
    """
    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return pd.read_sql_query(query, conn)
    except Exception as e:
        raise Exception(f"Error getting preview for table '{table_name}': {str(e)}")