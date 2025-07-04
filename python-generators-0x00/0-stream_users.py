#!/usr/bin/python3

import mysql.connector
import os

# Database configuration
# Ensure these match your MySQL setup. Recommended to use environment variables.
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'Bin@0911455745'), # Replace with your MySQL password
    'database': 'ALX_prodev'
}

def connect_to_prodev():
    """
    Establishes a connection to the ALX_prodev database.
    Returns the connection object or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database '{DB_CONFIG['database']}': {err}")
    return None

def stream_users():
    """
    A generator function that streams user data from the 'user_data' table
    in the 'ALX_prodev' database, yielding each row as a dictionary.

    Constraints:
    - Uses 'yield' for generator functionality.
    - Has no more than 1 explicit loop.
    - Automatically closes the cursor and connection upon completion or error.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if not connection:
            # If connection fails, the generator yields nothing and exits.
            print("Failed to establish database connection for streaming users.")
            return

        # Use dictionary=True to fetch rows directly as dictionaries
        cursor = connection.cursor(dictionary=True) 
        
        # Execute the query to select all user data
        cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id;")

        # Fetch and yield rows one by one using a single loop
        while True:
            row = cursor.fetchone()
            if row is None:
                break # Exit loop when no more rows are fetched
            yield row # Yield the fetched dictionary row
            
    except mysql.connector.Error as err:
        print(f"Database error during streaming: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure cursor and connection are closed in all cases
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        # print("Database connection and cursor closed.") # Optional: for debugging

# This block allows you to test the generator directly by running 0-stream_users.py
if __name__ == '__main__':
    print("--- Testing stream_users() directly (first 3 rows) ---")
    count = 0
    for user_record in stream_users():
        print(user_record)
        count += 1
        if count >= 3:
            break
    print("--- Direct test complete ---")
