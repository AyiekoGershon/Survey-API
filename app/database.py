"""
PostgreSQL Database Connection Module
Uses psycopg2 to connect to Supabase PostgreSQL
Provides mysql.connector-compatible interface for existing code
"""
import psycopg2
from psycopg2 import pool, extras
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
db_config: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "aws-1-eu-central-1.pooler.supabase.com"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres.yieipunlunexjrflrwau"),
    "password": os.getenv("DB_PASSWORD", "145Gershon#"),
    "database": os.getenv("DB_NAME", "postgres"),
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


class PatchedCursor:
    """Wrapper around psycopg2 cursor that supports mysql.connector-style interface"""
    def __init__(self, cursor, conn):
        self._cursor = cursor
        self._conn = conn
        self._lastrowid = None
        self._rowcount = -1

    def execute(self, query, params=None):
        # Convert MySQL-style %s placeholders to PostgreSQL-style $1, $2, etc.
        # But psycopg2 actually supports %s placeholders too, so we keep them.
        try:
            self._cursor.execute(query, params)
            self._rowcount = self._cursor.rowcount
            # For INSERT statements, fetch the last inserted ID
            query_upper = query.strip().upper()
            if query_upper.startswith("INSERT"):
                self._cursor.execute("SELECT LASTVAL()")
                result = self._cursor.fetchone()
                if result:
                    self._lastrowid = result[0]
            return self._cursor
        except Exception as e:
            raise e

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        self._cursor.close()

    @property
    def rowcount(self):
        return self._rowcount if self._rowcount >= 0 else self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._lastrowid


class PatchedDictCursor:
    """Wrapper around psycopg2 RealDictCursor that supports mysql.connector-style interface"""
    def __init__(self, cursor, conn):
        self._cursor = cursor
        self._conn = conn
        self._lastrowid = None
        self._rowcount = -1

    def execute(self, query, params=None):
        try:
            self._cursor.execute(query, params)
            self._rowcount = self._cursor.rowcount
            # For INSERT statements, fetch the last inserted ID
            query_upper = query.strip().upper()
            if query_upper.startswith("INSERT"):
                self._cursor.execute("SELECT LASTVAL()")
                result = self._cursor.fetchone()
                if result:
                    # RealDictCursor returns a dict
                    self._lastrowid = result.get("lastval", list(result.values())[0] if result else None)
            return self._cursor
        except Exception as e:
            raise e

    def fetchone(self):
        row = self._cursor.fetchone()
        if row:
            return dict(row)
        return None

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self._cursor.close()

    @property
    def rowcount(self):
        return self._rowcount if self._rowcount >= 0 else self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._lastrowid


class WrappedConnection:
    """Wrapper around psycopg2 connection to provide mysql.connector-compatible interface"""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False):
        if dictionary:
            real_cursor = self._conn.cursor(cursor_factory=extras.RealDictCursor)
            return PatchedDictCursor(real_cursor, self._conn)
        else:
            real_cursor = self._conn.cursor()
            return PatchedCursor(real_cursor, self._conn)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        pool = connection_pool
        if pool:
            pool.putconn(self._conn)


def get_db_connection() -> WrappedConnection:
    """Get a database connection from the pool"""
    if connection_pool is None:
        raise Exception("Database connection pool not initialized")
    conn = connection_pool.getconn()
    conn.autocommit = False
    return WrappedConnection(conn)


def init_database():
    """Initialize database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False
