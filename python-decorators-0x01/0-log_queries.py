import sqlite3
import functools
from datetime import datetime # <--- ADD THIS LINE

#### decorator to lof SQL queries

def log_queries(func):
    """
    A decorator that logs the SQL query executed by the decorated function.
    It expects the SQL query to be passed as a keyword argument named 'query'
    or as the first positional argument.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query_to_log = None

        # Try to find the query from keyword arguments first
        if 'query' in kwargs:
            query_to_log = kwargs['query']
        # Fallback: if 'query' not in kwargs, check if it's the first positional argument
        elif args and isinstance(args[0], str): # Check if the first arg is a string, likely the query
            query_to_log = args[0]

        if query_to_log:
            print(f"Executing query: {query_to_log}")
        else:
            # This case handles functions that might not have a clear 'query' argument,
            # or it's named differently. For this task, 'query' is expected.
            print(f"Logging: Executing function '{func.__name__}', no explicit 'query' argument found for logging.")

        # Call the original function with its arguments
        result = func(*args, **kwargs)
        return result
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database using the given query.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# --- For local testing: Database setup and example usage ---
# This part is for testing your code locally and would not necessarily be
# part of the submission file unless explicitly required for demonstration.

def setup_database(db_name='users.db'):
    """
    Sets up a simple SQLite database with a users table for testing.
    Inserts sample data if the table is empty.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    # Insert some dummy data, ignoring if they already exist
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (3, 'Charlie', 'charlie@example.com')")
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' and 'users' table ensured/setup.")

if __name__ == "__main__":
    setup_database()

    print("\n--- Fetching all users ---")
    users = fetch_all_users(query="SELECT * FROM users")
    print("Fetched users:", users)

    print("\n--- Fetching a specific user ---")
    specific_user = fetch_all_users(query="SELECT name, email FROM users WHERE id = 2")
    print("Fetched specific user:", specific_user)

    print("\n--- Testing with a query that might not return results ---")
    no_users = fetch_all_users(query="SELECT * FROM users WHERE name = 'NonExistent'")
    print("Fetched non-existent users:", no_users)

    # Example of how it would log if 'query' was passed positionally (though not the primary example)
    @log_queries
    def execute_arbitrary_sql(sql_command):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(sql_command)
        conn.commit() # For DML like INSERT/UPDATE/DELETE
        conn.close()
        return "Command executed."

    print("\n--- Testing with positional argument ---")
    execute_arbitrary_sql("INSERT OR IGNORE INTO users (id, name, email) VALUES (4, 'David', 'david@example.com')")
    print("After insert, re-fetching all users:")
    users_after_insert = fetch_all_users(query="SELECT * FROM users")
    print("Fetched users after insert:", users_after_insert)

