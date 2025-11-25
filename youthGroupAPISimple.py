
import mysql.connector
from mysql.connector import errorcode
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

def main():
    """
    Demonstrates basic database operations.
    """
    try:
        # Establish a connection to the database
        cnx = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME
        )
        print("Successfully connected to the database.")

        # Create a cursor
        cursor = cnx.cursor()

        # Execute a query
        query = "SELECT ID, firstName, lastName FROM Person ORDER BY lastName, firstName LIMIT 5;"
        cursor.execute(query)

        # Fetch and print the results
        print("\nFirst 5 people:")
        for (ID, firstName, lastName) in cursor.fetchall():
            print(f"  - [ID: {ID}] {firstName} {lastName}")

        # Close the cursor and connection
        cursor.close()
        cnx.close()
        print("\nConnection closed.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


if __name__ == '__main__':
    main()
