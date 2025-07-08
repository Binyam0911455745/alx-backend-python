import sqlite3
import functools
import logging
import sys

# Configure basic logging to stdout
# This will show the logged messages in your terminal
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

#### decorator to log SQL queries
def log_queries(func):
    """
    A decorator that logs the SQL query passed to the decorated function
    before the function is executed.

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        
        # Attempt to find the SQL query from function arguments
        # Check positional arguments first
        if args and isinstance(args[0], str): # Assuming query is the first string argument
            query = args[0]
        
        # Then check keyword arguments, which takes precedence if both exist
        if 'query' in kwargs:
            query = kwargs['query']

        if query:
            logging.info(f"Executing SQL query: {query}")
        else:
            logging.warning(f"Could not identify SQL query for function '{func.__name__}'. "
                            f"Arguments received: args={args}, kwargs={kwargs}")

        # Execute the original function and return its result
        return func(*args, **kwargs)
    return wrapper

# --- Provided example function and usage ---

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the 'users' table using the provided query.
    This function's execution will be logged by the @log_queries decorator.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# --- Helper function to set up the SQLite database for testing ---
def setup_db():
    """
    Sets up a simple SQLite 'users.db' database with a 'users' table
    and inserts some sample data if the table is empty.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()

    # Insert some dummy data if the table is empty
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Bob Williams', 'bob@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Charlie Brown', 'charlie@example.com')")
        conn.commit()
        logging.info("Sample data inserted into 'users' table.")
    except sqlite3.IntegrityError:
        logging.info("Sample data already exists in 'users' table (or email unique constraint violated).")
    except Exception as e:
        logging.error(f"Error inserting sample data: {e}")
    finally:
        conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Ensure the database and table are set up
    setup_db()

    # 2. Fetch users while logging the query
    print("\n--- Calling fetch_all_users with a SELECT * query ---")
    users = fetch_all_users(query="SELECT * FROM users")
    print("Fetched users count:", len(users))
    for user in users:
        print(user)

    print("\n--- Calling fetch_all_users with a specific SELECT query ---")
    specific_user = fetch_all_users(query="SELECT name, email FROM users WHERE id = 1")
    print("Fetched specific user:", specific_user)

    print("\n--- Example with query as positional argument (also works) ---")
    users_positional = fetch_all_users("SELECT id, name FROM users")
    print("Fetched users (positional query):", users_positional)

    # Example of a function that doesn't easily expose a 'query' argument for the decorator
    @log_queries
    def another_db_op(table_name, condition):
        # This function won't log a query via the decorator's current logic,
        # unless 'query' is passed explicitly or its first arg is the query.
        logging.info(f"Inside another_db_op with table: {table_name}, condition: {condition}")
        # A real implementation would form and execute the query here.
        # For demonstration, we're just showing the decorator's logging limitation here.
        return f"Operation on {table_name} with {condition}"

    print("\n--- Calling another_db_op (demonstrating query detection) ---")
    result_op = another_db_op("products", "status='active'")
    print("another_db_op result:", result_op)

