"""
database.py - Database Connection Management Module

This module manages connections to three different database systems:
1. MySQL - Relational database for structured data (people, events, registrations)
2. MongoDB - NoSQL database for flexible, document-based data (event types, notes)
3. Redis - In-memory cache/database for real-time data (live check-ins)

Key Concepts:
- Connection Pooling: MySQL uses a connection pool to reuse connections efficiently
- Singleton Pattern: Each database client is created once and reused (global variables)
- Lazy Initialization: Connections are only created when first needed
- Graceful Shutdown: Properly closes connections when the application shuts down

Why use different databases?
- MySQL: Best for structured, relational data with complex queries and joins
- MongoDB: Best for flexible schemas that may vary (event types can have different fields)
- Redis: Best for fast, real-time data that needs to be accessed quickly (check-ins)
"""

import mysql.connector.pooling
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import redis

import os
import warnings

# --- Secret Management ---
# Import database credentials from config.py (keeps secrets separate from code)
from backend.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, MONGO_URI, MONGO_DB_NAME, REDIS_HOST, REDIS_PORT, REDIS_SSL, REDIS_PASSWORD, REDIS_USERNAME

# --- Connection Clients / Pools ---
# Global variables to store database connections (singleton pattern)
# These are initialized once and reused throughout the application lifecycle
db_pool = None          # MySQL connection pool (reuses connections efficiently)
mongo_client = None     # MongoDB client (single connection to MongoDB cluster)
redis_client = None     # Redis client (single connection to Redis server)

def get_mysql_pool():
    """
    Initializes and returns the MySQL connection pool.
    
    Connection Pooling:
    - Instead of creating a new connection for each database query, we create a pool
    - The pool maintains 5 connections that can be reused
    - When you need a connection, you borrow one from the pool
    - When done, you return it to the pool (not closed)
    - This is MUCH faster than creating/closing connections repeatedly
    
    Returns:
        MySQLConnectionPool: A pool of MySQL connections ready to use
    """
    global db_pool  # Access the global variable to store the pool
    
    # Lazy initialization: only create pool if it doesn't exist yet
    if db_pool is None:
        try:
            # Create a connection pool with 5 pre-allocated connections
            db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="fastapi_pool",  # Name for this pool (useful if you have multiple pools)
                pool_size=5,               # Maximum number of connections in the pool
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME            # Name of the database to connect to
            )
            print("Database connection pool created successfully.")
        except mysql.connector.Error as err:
            # can't run without database
            print(f"Error creating connection pool: {err}")
            exit()
    return db_pool  # Return the existing pool (or newly created one)

def get_mongo_client():
    """
    Initializes and returns the MongoDB client.
    
    MongoDB Connection Explained:
    - MongoDB uses a single client connection that manages multiple operations internally
    - The MONGO_URI contains connection string (like: mongodb+srv://user:pass@cluster.mongodb.net/)
    - ServerApi('1') specifies we want to use MongoDB API version 1 (stable)
    - We ping the server to verify the connection works before proceeding
    
    Returns:
        MongoClient: A client connection to MongoDB that can access databases/collections
    """
    global mongo_client  # Access the global variable
    
    # Lazy initialization: only create client if it doesn't exist yet
    if mongo_client is None:
        try:
            # Create MongoDB client with connection string and API version
            mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
            
            # Send a ping command to verify connection works
            # This is like saying "hello, are you there?" to the database
            mongo_client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            # If connection fails, print error and exit
            print(f"Error connecting to MongoDB: {e}")
            exit()
    return mongo_client  # Return the existing client (or newly created one)

def get_redis_client():
    """
    Initializes and returns the Redis client.
    
    Redis Connection Explained:
    - Redis is an in-memory data store (very fast, but data is lost on restart)
    - Used for caching and real-time data (like live check-ins)
    - decode_responses=True means Redis returns strings instead of bytes (easier to work with)
    - We ping to verify the connection works
    
    Returns:
        Redis: A client connection to Redis that can execute Redis commands
    """
    global redis_client  # Access the global variable
    
    # Lazy initialization: only create client if it doesn't exist yet
    if redis_client is None:
        try:
            # Create Redis client with connection details
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,      # Return strings instead of bytes (Python 3 friendly)
                username=REDIS_USERNAME,
                password=REDIS_PASSWORD,
            )
            # Ping Redis to verify connection works
            redis_client.ping()
            print("Successfully connected to Redis!")
        except Exception as e:
            # If connection fails, print error and exit
            print(f"Error connecting to Redis: {e}")
            exit()
    return redis_client  # Return the existing client (or newly created one)

# --- Functions to be called from the FastAPI app ---
# These are the main functions used by the API endpoints

def get_db_connection():
    """
    Gets a single connection from the MySQL connection pool.
    
    How it works:
    1. Gets the connection pool (creates it if needed)
    2. Borrows one connection from the pool
    3. Returns that connection for use
    
    IMPORTANT: You MUST close this connection when done (cursor.close() and cnx.close())
    Closing returns it to the pool, it doesn't destroy it!
    
    Returns:
        MySQL connection: A single database connection ready to execute queries
    """
    pool = get_mysql_pool()  # Get or create the connection pool
    return pool.get_connection()  # Borrow one connection from the pool

def get_mongo_db():
    """
    Gets the MongoDB database instance.
    
    How it works:
    - MongoDB organizes data into databases (like MySQL)
    - Each database contains collections (like tables in MySQL)
    - This returns a database object you can use to access collections
    
    Example usage:
        db = get_mongo_db()
        collection = db["eventTypes"]  # Access a collection
        docs = collection.find({})     # Query documents
    
    Returns:
        Database: A MongoDB database object for accessing collections
    """
    client = get_mongo_client()  # Get or create the MongoDB client
    return client[MONGO_DB_NAME]  # Access the specific database by name

def get_redis_conn():
    """
    Gets the Redis client instance.
    
    How it works:
    - Redis doesn't have databases like MySQL/MongoDB
    - You use the client directly to execute Redis commands
    - Commands like: SET, GET, SADD, SMEMBERS, HSET, HGETALL
    
    Example usage:
        r = get_redis_conn()
        r.set("key", "value")      # Store a string
        r.sadd("set_key", "item")  # Add to a set
        r.hset("hash_key", "field", "value")  # Add to a hash
    
    Returns:
        Redis: A Redis client ready to execute commands
    """
    return get_redis_client()  # Get or create the Redis client

# --- Graceful Shutdown ---
def close_connections():
    """
    Closes all database connections gracefully when the application shuts down.
    
    Why this matters:
    - Properly closing connections prevents resource leaks
    - Ensures data is flushed and transactions are committed
    - Good practice for production applications
    
    Note:
    - MySQL: Connections in the pool are automatically cleaned up when pool is destroyed
    - MongoDB: Client connection should be explicitly closed
    - Redis: Connection cleanup is handled automatically, but closing is good practice
    """
    global mongo_client
    
    # Close MongoDB client if it exists
    # This ensures any pending operations complete and connection is properly terminated
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")
    
    # Note: MySQL pool connections are managed automatically
    # When the application exits, the pool is destroyed and connections are closed
    
    # Note: Redis client cleanup is handled automatically by the library
    # Explicit closing isn't required but can be done if needed
    
    print("Connection cleanup finished.")

# Example of how to use the functions
if __name__ == "__main__":
    print("Attempting to connect to all databases...")
    get_mysql_pool()
    get_mongo_client()
    # get_redis_client()
    print("\nAll database connections seem to be configured correctly.")
    print("This script is for setting up connections. Run the main FastAPI app to start the server.")
    close_connections()
