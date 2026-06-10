"""
PostgreSQL Database Connection Module
Use this instead of database.py when using PostgreSQL
"""

import psycopg2
from psycopg2 import pool, extensions
from typing import Dict, Any, Any as PSQLConnection
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "sky_survey_db"),
}

# Create connection pool
try:
    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=int(os.getenv("DB_POOL_SIZE", 10)),
        **db_config
    )
    print("Database connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")
    connection_pool = None


def get_db_connection() -> psycopg2.extensions.connection:
    """Get a database connection from the pool"""
    if connection_pool is None:
        raise Exception("Database connection pool not initialized")
    conn = connection_pool.getconn()
    # Set connection to return dict-like cursor by default
    conn.autocommit = False
    return conn


def return_db_connection(conn: psycopg2.extensions.connection) -> None:
    """Return a connection to the pool"""
    if connection_pool and conn:
        connection_pool.putconn(conn)


def get_dict_cursor(conn: psycopg2.extensions.connection):
    """Get a cursor that returns rows as dictionaries"""
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cur


def init_database() -> bool:
    """Initialize and test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        return_db_connection(conn)
        return result is not None
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False


# For compatibility with existing code that expects cursor(dictionary=True)
class CursorWrapper:
    """Wrapper to make dict cursors compatible with mysql.connector style"""
    def __init__(self, cursor):
        self.cursor = cursor
    
    def execute(self, query, params=None):
        return self.cursor.execute(query, params)
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    def close(self):
        return self.cursor.close()
    
    @property
    def rowcount(self):
        return self.cursor.rowcount
    
    @property
    def lastrowid(self):
        # PostgreSQL uses RETURNING clause instead
        # This is a fallback, typically not used
        return None


# Import psycopg2.extras for DictCursor
try:
    import psycopg2.extras
except ImportError:
    print("Warning: psycopg2.extras not available")
