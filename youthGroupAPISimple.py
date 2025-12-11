"""
youthGroupAPISimple.py - Simple Database Connection Demo

This is a simple demonstration script showing basic MySQL database operations.
It's a minimal example that shows:
1. How to connect to MySQL
2. How to execute a SELECT query
3. How to fetch and process results
4. How to handle errors
5. How to properly close connections

This is different from database.py because:
- database.py uses connection pooling (for production)
- This script uses a simple direct connection (for learning)

Use this script to:
- Test your database connection
- Understand basic MySQL operations
- Learn error handling patterns
"""

import mysql.connector
from mysql.connector import errorcode
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

def main():
    """
    Demonstrates basic database operations.
    
    This function shows the fundamental steps of database interaction:
    1. Connect to database
    2. Create cursor (used to execute queries)
    3. Execute SQL query
    4. Fetch results
    5. Process results
    6. Close cursor and connection
    
    Note: In production (youthGroupFastAPI.py), we use connection pooling
    instead of creating/closing connections for each operation.
    """
    try:
        # Establish a connection to the database
        # This creates a new connection each time (not efficient for many requests)
        # In production, use connection pooling (see database.py)
        cnx = mysql.connector.connect(
            user=DB_USER,        # Database username from config
            password=DB_PASSWORD, # Database password from config
            host=DB_HOST,         # Database server address
            database=DB_NAME       # Name of the database to use
        )
        print("Successfully connected to the database.")

        # Create a cursor
        # A cursor is like a "pointer" that executes SQL commands and fetches results
        # dictionary=True would return results as dictionaries, but we're using tuples here
        cursor = cnx.cursor()

        # Execute a SELECT query
        # This query gets the first 5 people, ordered by last name then first name
        # LIMIT 5 restricts results to 5 rows
        query = "SELECT ID, firstName, lastName FROM Person ORDER BY lastName, firstName LIMIT 5;"
        cursor.execute(query)  # Execute the SQL query

        # Fetch and print the results
        # fetchall() retrieves all rows returned by the query
        # Results are returned as tuples: (ID, firstName, lastName)
        print("\nFirst 5 people:")
        for (ID, firstName, lastName) in cursor.fetchall():
            # Unpack tuple into variables and print formatted output
            print(f"  - [ID: {ID}] {firstName} {lastName}")

        # Close the cursor and connection
        # IMPORTANT: Always close connections when done to free resources
        cursor.close()  # Close cursor first
        cnx.close()     # Then close connection
        print("\nConnection closed.")

    except mysql.connector.Error as err:
        # Handle MySQL-specific errors
        # errorcode constants help identify specific error types
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            # Wrong username or password
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            # Database doesn't exist
            print("Database does not exist")
        else:
            # Some other MySQL error - print the error message
            print(err)


if __name__ == '__main__':
    # Only run main() if script is executed directly (not imported)
    # This allows the script to be imported without automatically running
    main()
