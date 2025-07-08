import sqlite3
import logging
import sys

# Configure basic logging to stdout for clarity and debugging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper function to set up the SQLite database for testing ---
def setup_db(db_name='users.db'):
    """
    Sets up a simple SQLite database with a 'users' table and inserts sample data.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
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
                logging.info("Sample data inserted into 'users' table during setup.")
            except sqlite3.IntegrityError:
                logging.info("Sample data already exists during setup (email unique constraint violated).")
            except Exception as e:
                logging.error(f"Error inserting sample data during setup: {e}", exc_info=True)
        else:
            logging.info("Users table already contains data, skipping sample insertion during setup.")
            
    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Custom class-based context manager for Database connection ---
class DatabaseConnection:
    """
    A class-based context manager for managing SQLite database connections.
    It ensures the database connection is automatically opened when entering
    the 'with' block and closed when exiting it, even if errors occur.
    """
    def __init__(self, db_name):
        """
        Initializes the context manager with the database file name.
        """
        self.db_name = db_name
        self.conn = None # Connection object, will be set in __enter__

    def __enter__(self):
        """
        Opens the database connection and returns the connection object.
        This method is called automatically when the 'with' statement is entered.
        """
        logging.info(f"Entering context: Opening database connection to '{self.db_name}'...")
        try:
            self.conn = sqlite3.connect(self.db_name)
            return self.conn # The returned object is assigned to the 'as' variable
        except sqlite3.Error as e:
            logging.error(f"Failed to open database connection: {e}", exc_info=True)
            raise # Re-raise the exception if connection fails

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection.
        This method is called automatically when the 'with' block is exited,
        whether normally or due to an exception.

        Args:
            exc_type: The type of exception (e.g., ValueError, sqlite3.Error). None if no exception.
            exc_val: The exception instance. None if no exception.
            exc_tb: A traceback object. None if no exception.
        """
        if self.conn:
            logging.info(f"Exiting context: Closing database connection to '{self.db_name}'.")
            self.conn.close()
        
        # If an exception occurred within the 'with' block, log it.
        # Returning False (or None) from __exit__ will re-raise the exception.
        # Returning True would suppress it. We want it to propagate for visibility.
        if exc_type:
            logging.error(f"An exception occurred inside the 'with' block: {exc_val}", exc_info=True)
        return False # Propagate any exception that occurred

# --- Main execution block for demonstrating usage ---
if __name__ == "__main__":
    db_file = 'users.db'
    setup_db(db_file) # Ensure the database is set up with sample data

    print("\n--- Test Case 1: Successful Query using DatabaseConnection ---")
    try:
        # Use the custom context manager with the 'with' statement
        with DatabaseConnection(db_file) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users"
            logging.info(f"Executing query: {query}")
            cursor.execute(query)
            results = cursor.fetchall()
            print("Query results (SELECT * FROM users):")
            for row in results:
                print(row)
        print("--> Database connection successfully closed after query (check logs above).")
    except Exception as e:
        print(f"An unexpected error occurred during Test Case 1: {e}")

    print("\n--- Test Case 2: Query with Simulated Error using DatabaseConnection ---")
    try:
        with DatabaseConnection(db_file) as conn:
            cursor = conn.cursor()
            # Simulate an invalid query to trigger an error
            invalid_query = "SELECT * FROM non_existent_table"
            logging.info(f"Attempting invalid query: {invalid_query}")
            cursor.execute(invalid_query) # This will raise sqlite3.OperationalError
            results_error = cursor.fetchall() # This line won't be reached
            print("Query results (should not reach here):", results_error)
        print("--> This line should not be printed if error propagates correctly.")
    except sqlite3.OperationalError as e:
        print(f"Caught expected error: {e}")
        print("--> Database connection should still be closed by context manager (check logs above).")
    except Exception as e:
        print(f"Caught an unexpected error type: {type(e).__name__}: {e}")

    print("\n--- Test Case 3: Verify connection closure (conceptual) ---")
    print("Check log messages above for 'Closing database connection'.")
    print("The primary benefit of 'with' is guaranteed resource cleanup.")
    # You cannot directly access 'conn' here as it's out of scope/closed by __exit__.
    # The log messages are the best indication of correct behavior.

