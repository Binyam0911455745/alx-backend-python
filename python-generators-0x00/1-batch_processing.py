#!/usr/bin/python3

import mysql.connector
import os
import sys

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

def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows from the 'user_data' table in batches.
    Yields each batch as a list of dictionaries.

    Args:
        batch_size (int): The number of rows to fetch per batch.

    Constraints:
    - Uses 'yield' to return batches.
    - Contains no more than 1 loop.
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer.")

    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if not connection:
            print("Failed to establish database connection for batch streaming.", file=sys.stderr)
            return # Generator yields nothing if connection fails

        # Use dictionary=True to fetch rows directly as dictionaries
        # Use buffered=False for true unbuffered streaming,
        # otherwise all results might be loaded into client memory before yielding.
        cursor = connection.cursor(dictionary=True, buffered=False) 
        
        # Execute the query to select all user data
        cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id;")

        # Loop 1: Fetch and yield batches
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch: # If the batch is empty, no more data
                break 
            yield batch
            
    except mysql.connector.Error as err:
        print(f"Database error during batch streaming: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during batch streaming: {e}", file=sys.stderr)
    finally:
        # Ensure cursor and connection are closed in all cases
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        # print("Database connection and cursor closed after batch streaming.") # Optional: for debugging

def batch_processing(batch_size):
    """
    Generator function that processes users in batches, filtering those over age 25.
    Yields each filtered user as a dictionary.

    Args:
        batch_size (int): The size of batches to process.

    Constraints:
    - Uses 'yield' to return processed users.
    - Combined with stream_users_in_batches, total loops <= 3.
    """
    # Loop 2: Iterate over batches provided by the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Iterate over users within the current batch
        for user in batch:
            if user.get('age') is not None and user['age'] > 25:
                yield user

# This block allows you to test the batch_processing directly
if __name__ == '__main__':
    print("--- Testing batch_processing(batch_size=3) directly (first few filtered users) ---")
    
    # Simulate database population if running this directly without 0-main.py
    # from your previous seed.py, you would call:
    # import seed # Assuming seed.py is accessible
    # conn_seed = seed.connect_db()
    # if conn_seed:
    #     seed.create_database(conn_seed)
    #     conn_seed.close()
    #     conn_seed_prodev = seed.connect_to_prodev()
    #     if conn_seed_prodev:
    #         seed.create_table(conn_seed_prodev)
    #         seed.insert_data(conn_seed_prodev, 'user_data.csv')
    #         conn_seed_prodev.close()
    # else:
    #    print("Could not set up database for direct test. Ensure MySQL is running.")

    processed_count = 0
    # The batch_processing function itself is a generator, so we iterate over it
    for user_data in batch_processing(batch_size=3):
        print(user_data)
        processed_count += 1
        if processed_count >= 10: # Limit output for direct test
            break
    print("--- Direct test complete ---")
