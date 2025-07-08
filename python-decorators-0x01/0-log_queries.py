import sqlite3
import functools
import logging
import sys

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

#### decorator to log SQL queries
def log_queries(func):
    """
    A decorator that logs the SQL query passed to the decorated function
    before the function is executed.

    Assumes the decorated function takes the SQL query as its first
    positional argument or as a keyword argument named 'query'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        
        # Attempt to find the SQL query from function arguments
        # Check positional arguments first (assuming it's a string, typically the first arg)
        if args and isinstance(args[0], str): 
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

# --- Provided example function from the task description ---

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
    conn = None # Initialize conn to None
    try:
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
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            try:
                cursor.execute("INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com')")
                cursor.execute("INSERT INTO users (name, email) VALUES ('Bob Williams', 'bob@example.com')")
                cursor.execute("INSERT INTO users (name, email) VALUES ('Charlie Brown', 'charlie@example.com')")
                conn.commit()
                logging.info("Sample data inserted into 'users' table.")
            except sqlite3.IntegrityError:
                logging.info("Sample data already exists in 'users' table (or email unique constraint violated).")
            except Exception as e:
                logging.error(f"Error inserting sample data during setup: {e}", exc_info=True)
        else:
            logging.info("Users table already contains data, skipping sample insertion during setup.")

    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Ensure the database and table are set up for testing
    setup_db()

    # 2. Fetch users while logging the query
    print("\n--- Calling fetch_all_users with a SELECT * query ---")
    users = fetch_all_users(query="SELECT * FROM users")
    print("Fetched users count:", len(users))
    for user in users:
        print(user)

    print("\n--- Calling fetch_all_users with a specific SELECT query ---")
    user_by_id = fetch_all_users(query="SELECT name, email FROM users WHERE id = 1")
    print("Fetched specific user (ID 1):", user_by_id)

    print("\n--- Example with query as positional argument (also works) ---")
    users_positional = fetch_all_users("SELECT id, name FROM users ORDER BY id DESC")
    print("Fetched users (positional query):", users_positional)

    # Example of a function that doesn't explicitly expose a 'query' argument
    # (Note: This will trigger the WARNING in the decorator's log because 'query' isn't explicitly found)
    @log_queries
    def process_data(table_name, filter_param):
        logging.info(f"Inside process_data for table: {table_name}, filter: {filter_param}")
        # In a real scenario, the query might be constructed here, not passed in.
        # For this demo, the decorator won't find a direct 'query' argument.
        return f"Processed data for {table_name} with filter {filter_param}"

    print("\n--- Calling process_data (demonstrating query detection limitation) ---")
    # This call will NOT cause a TypeError, but the decorator will log a WARNING
    # because it won't find a 'query' argument.
    result_process = process_data("products", "active") 
    print("process_data result:", result_process)
