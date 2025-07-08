import sqlite3
import functools
import logging
import sys

# Configure basic logging for clarity
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

def with_db_connection(func):
    """
    A decorator that automatically opens a SQLite database connection ('users.db'),
    passes the connection object as the first argument to the decorated function,
    and ensures the connection is closed afterwards, regardless of success or failure.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # Open the database connection
            logging.info("Opening database connection...")
            conn = sqlite3.connect('users.db')
            
            # Pass the connection as the first argument to the decorated function
            # The decorated function (e.g., get_user_by_id) must accept 'conn' as its first parameter.
            result = func(conn, *args, **kwargs)
            
            return result
        except sqlite3.Error as e:
            # Log specific SQLite errors
            logging.error(f"Database error during execution of '{func.__name__}': {e}", exc_info=True)
            # Re-raise the exception so the calling code can handle it
            raise
        except Exception as e:
            # Log any other unexpected errors
            logging.error(f"An unexpected error occurred during execution of '{func.__name__}': {e}", exc_info=True)
            raise
        finally:
            # Ensure the connection is closed even if an error occurred
            if conn:
                logging.info("Closing database connection.")
                conn.close()
    return wrapper

# --- Provided example function from the task description ---

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a user by ID using the provided database connection.
    This function expects the connection object as its first argument.
    """
    logging.info(f"Executing query for user_id={user_id}")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

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
                -- Add other columns if needed for other tasks
            )
        ''')
        conn.commit()

        # Insert some dummy data if the the table is empty or has less than 2 users
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count < 2: # Ensure at least two users for testing
            try:
                cursor.execute("INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com')")
                cursor.execute("INSERT INTO users (name, email) VALUES ('Bob Williams', 'bob@example.com')")
                conn.commit()
                logging.info("Sample data inserted into 'users' table.")
            except sqlite3.IntegrityError:
                logging.info("Sample data already exists (email unique constraint violated).")
            except Exception as e:
                logging.error(f"Error inserting sample data: {e}")
        else:
            logging.info("Users table already contains data, skipping sample insertion.")
            
    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Ensure the database and table are set up for testing
    setup_db()

    # 2. Fetch user by ID with automatic connection handling
    print("\n--- Fetching user with ID = 1 ---")
    user_1 = get_user_by_id(user_id=1)
    print("User found (ID 1):", user_1)

    print("\n--- Fetching user with ID = 2 ---")
    user_2 = get_user_by_id(user_id=2)
    print("User found (ID 2):", user_2)

    print("\n--- Fetching user with ID = 99 (non-existent) ---")
    user_none = get_user_by_id(user_id=99)
    print("User found (ID 99):", user_none)

    print("\n--- Demonstrating error handling with a malformed query ---")
    @with_db_connection
    def execute_bad_query(conn):
        """Attempts to execute a syntactically incorrect SQL query."""
        logging.info("Attempting a malformed query within execute_bad_query...")
        cursor = conn.cursor()
        # This query will cause an error
        cursor.execute("SELECT non_existent_column FROM users_table_does_not_exist") 
        return cursor.fetchall()
    
    try:
        execute_bad_query()
    except sqlite3.OperationalError as e:
        print(f"\nSuccessfully caught expected OperationalError: {e}")
    except Exception as e:
        print(f"\nCaught unexpected error: {e}")
