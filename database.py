import mysql.connector.pooling
from pymongo import MongoClient
from pymongo.server_api import ServerApi
# import redis

import os
import warnings

# --- Secret Management ---
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, MONGO_URI, MONGO_DB_NAME

# --- Connection Clients / Pools ---
db_pool = None
mongo_client = None
redis_client = None

def get_mysql_pool():
    """Initializes and returns the MySQL connection pool."""
    global db_pool
    if db_pool is None:
        try:
            db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="fastapi_pool",
                pool_size=5,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME
            )
            print("Database connection pool created successfully.")
        except mysql.connector.Error as err:
            print(f"Error creating connection pool: {err}")
            exit()
    return db_pool

def get_mongo_client():
    """Initializes and returns the MongoDB client."""
    global mongo_client
    if mongo_client is None:
        try:
            mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
            # Send a ping to confirm a successful connection
            mongo_client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            exit()
    return mongo_client

# def get_redis_client():
#     """Initializes and returns the Redis client."""
#     global redis_client
#     if redis_client is None:
#         try:
#             redis_client = redis.Redis(
#                 host=REDIS_HOST,
#                 port=REDIS_PORT,
#                 decode_responses=True,
#                 username=REDIS_USERNAME,
#                 password=REDIS_PASSWORD,
#             )
#             # Check connection
#             redis_client.ping()
#             print("Successfully connected to Redis!")
#         except Exception as e:
#             print(f"Error connecting to Redis: {e}")
#             exit()
#     return redis_client

# --- Functions to be called from the FastAPI app ---
def get_db_connection():
    """Gets a connection from the MySQL pool."""
    pool = get_mysql_pool()
    return pool.get_connection()

def get_mongo_db():
    """Gets the MongoDB database instance."""
    client = get_mongo_client()
    return client[MONGO_DB_NAME]

# def get_redis_conn():
#     """Gets the Redis client instance."""
#     return get_redis_client()

# --- Graceful Shutdown ---
def close_connections():
    """Close all database connections."""
    # MySQL pool doesn't have an explicit close, connections are returned to pool.
    # MongoDB client should be closed if the app is shutting down.
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")
    # Redis client doesn't require explicit closing for this library version
    # when used like this, but it's good practice if a close method is available.
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
