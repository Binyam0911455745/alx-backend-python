#!/usr/bin/python3

import mysql.connector
import os
import sys
from decimal import Decimal # To handle Decimal types from MySQL

# Database configuration (copied for self-containment in this script)
# Ensure these match your MySQL setup.
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
        print(f"Error connecting to database '{DB_CONFIG['database']}': {err}", file=sys.stderr)
    return None

def stream_user_ages():
    """
    Generator function that streams user ages one by one from the 'user_data' table.
    Yields each age as a float.

    Constraints:
    - Uses 'yield' to return ages.
    - Contains exactly 1 loop.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if not connection:
            print("Failed to establish database connection for streaming ages.", file=sys.stderr)
            return # Generator yields nothing if connection fails

        # We only need the 'age' column
        cursor = connection.cursor(buffered=False) # Use unbuffered for true streaming
        cursor.execute("SELECT age FROM user_data;")

        # Loop 1: Fetch and yield ages one by one
        while True:
            row = cursor.fetchone()
            if row is None:
                break # No more ages
            
            age = row[0] # The age is the first (and only) element in the tuple
            
            # Ensure age is a float, handling Decimal type from MySQL
            if isinstance(age, Decimal):
                yield float(age)
            else:
                yield age # Yield as is if not Decimal (e.g., already float or int)
            
    except mysql.connector.Error as err:
        print(f"Database error during age streaming: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during age streaming: {e}", file=sys.stderr)
    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Main execution block to calculate average age
if __name__ == '__main__':
    total_age = 0.0
    user_count = 0

    # Loop 2: Iterate over the generator to get ages one by one
    print("Calculating average age...")
    for age in stream_user_ages():
        total_age += age
        user_count += 1
    
    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age:.2f}") # Format to 2 decimal places
    else:
        print("No user data found to calculate average age.")
