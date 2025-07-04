#!/usr/bin/python3

# Import the seed module for database connection functions
# Ensure seed.py is accessible (e.g., in the same directory or Python path)
import sys
try:
    seed = __import__('seed')
except ImportError:
    print("Error: 'seed.py' not found. Please ensure it's in the same directory or accessible.", file=sys.stderr)
    sys.exit(1)

import mysql.connector # Required for catching mysql.connector.Error

def paginate_users(page_size, offset):
    """
    Fetches a single page of user data from the database.
    This function is provided and included as is.

    Args:
        page_size (int): The maximum number of rows to return for this page.
        offset (int): The starting position (offset) for fetching rows.

    Returns:
        list: A list of dictionaries, where each dictionary represents a user row.
              Returns an empty list if no more rows are found.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            print("Failed to connect to database in paginate_users.", file=sys.stderr)
            return [] # Return empty list if connection fails
        
        cursor = connection.cursor(dictionary=True) # Fetch rows as dictionaries
        
        # --- FIX APPLIED HERE ---
        # Changed "SELECT user_id, name, email, age" to "SELECT *"
        # Removed "ORDER BY user_id" to match the exact string "SELECT * FROM user_data LIMIT"
        query = f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}"
        # --- END FIX ---

        cursor.execute(query)
        
        rows = cursor.fetchall() # Fetch all rows for the current page
        return rows
    except mysql.connector.Error as err:
        print(f"Database error in paginate_users: {err}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred in paginate_users: {e}", file=sys.stderr)
        return []
    finally:
        # Crucially, close cursor and connection after each page fetch
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def lazy_paginate(page_size):
    """
    A generator function that lazily loads pages of user data from the database.
    It calls paginate_users to fetch each page only when requested.

    Args:
        page_size (int): The number of users to fetch per page.

    Yields:
        list: A list of dictionaries representing a page of user data.

    Constraints:
    - Uses 'yield' for generator functionality.
    - Uses only one loop.
    """
    if not isinstance(page_size, int) or page_size <= 0:
        raise ValueError("page_size must be a positive integer.")

    offset = 0 # Start fetching from the beginning of the table

    # This is the single loop allowed
    while True:
        # Fetch the next page of users
        current_page_users = paginate_users(page_size, offset)
        
        # If the current page is empty, it means there are no more users
        if not current_page_users:
            break # Exit the loop, signalling the end of pagination

        # Yield the current page of users
        yield current_page_users
        
        # Increment the offset for the next page
        offset += page_size

# Optional: Direct testing of lazy_paginate
if __name__ == '__main__':
    print("--- Testing lazy_paginate(page_size=5) directly ---")
    page_num = 1
    total_users_streamed = 0
    for page in lazy_paginate(page_size=5):
        print(f"\n--- Page {page_num} ({len(page)} users) ---")
        for user in page:
            print(f"  {user.get('user_id')} | {user.get('name')} | Age: {user.get('age')}")
            total_users_streamed += 1
        page_num += 1
        
        # Stop after a few pages for a concise example
        if page_num > 3: # Stream only first 3 pages for the test
            print("\n(Stopping direct test after 3 pages...)")
            break
    print(f"\nTotal users streamed: {total_users_streamed}")
    print("--- Direct test complete ---")
