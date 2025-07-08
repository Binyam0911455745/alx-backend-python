import sqlite3
import logging
import sys

# Configure basic logging to stdout for clarity and debugging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper function to set up the SQLite database for testing ---
def setup_db(db_name='users.db'):
    """
    Sets up a simple SQLite database with a 'users' table (including 'age')
    and inserts sample data if the table is empty or needs more data.
    It drops the table if it exists to ensure a clean schema for testing.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # --- IMPORTANT CHANGE: Drop the table if it exists to ensure fresh schema ---
        logging.info("Dropping existing 'users' table if it exists to ensure fresh schema.")
        cursor.execute('DROP TABLE IF EXISTS users')
        conn.commit()

        # Create users table with an 'age' column
        cursor.execute('''
            CREATE TABLE users ( -- Removed IF NOT EXISTS because we just dropped it
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER
            )
        ''')
        conn.commit()
        logging.info("Created 'users' table with 'age' column.")

        # Insert sample data
        users_to_insert = [
            ('Alice Johnson', 'alice@example.com', 30),
            ('Bob Williams', 'bob@example.com', 22),
            ('Charlie Brown', 'charlie@example.com', 35),
            ('David Lee', 'david.lee@example.com', 28),
            ('Eve Davis', 'eve@example.com', 40),
            ('Frank Green', 'frank@example.com', 20)
        ]
        
        inserted_count = 0
        for name, email, age in users_to_insert:
            try:
                cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (name, email, age))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # This would typically not happen after dropping, but good practice for robustness
                logging.warning(f"Skipping insert for {name} ({email}) due to existing unique email.")
        conn.commit()
        logging.info(f"Inserted {inserted_count} new sample users into 'users' table during setup.")
            
    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Custom class-based context manager for executing queries ---
class ExecuteQuery:
    """
    A class-based context manager that connects to a SQLite database,
    executes a given SQL query with optional parameters, fetches the results,
    and ensures the connection and cursor are closed upon exit.
    """
    def __init__(self, db_name, query, params=None):
        """
        Initializes the context manager with the database file name,
        the SQL query string, and optional parameters.

        Args:
            db_name (str): The name of the SQLite database file.
            query (str): The SQL query string to execute.
            params (tuple/list, optional): Parameters for the query. Defaults to None.
                                          Will be converted to an empty tuple if None.
        """
        self.db_name = db_name
        self.query = query
        # Ensure params is an iterable, even if None is provided
        self.params = params if params is not None else () 
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """
        Establishes database connection, creates a cursor, executes the query,
        fetches results, and returns the fetched results.
        This method is automatically called when entering the 'with' statement.
        """
        logging.info(f"Entering context: Preparing to execute query: '{self.query}' with params: {self.params}")
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            
            # Execute the query, using parameters if provided
            if self.params:
                self.cursor.execute(self.query, self.params)
            else:
                self.cursor.execute(self.query)
            
            # Fetch all results from the executed query
            self.results = self.cursor.fetchall()
            logging.info(f"Query executed successfully. Fetched {len(self.results)} row(s).")
            return self.results # The results object is assigned to the 'as' variable
        
        except sqlite3.Error as e:
            logging.error(f"Database error during query execution: {e}", exc_info=True)
            raise # Re-raise database-specific errors (e.g., table not found, syntax error)
        except Exception as e:
            logging.error(f"An unexpected error occurred during query execution: {e}", exc_info=True)
            raise # Re-raise any other unexpected errors

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database cursor and connection, ensuring proper resource cleanup.
        This method is automatically called when exiting the 'with' block,
        whether it exits normally or due to an exception.

        Args:
            exc_type: The type of exception raised in the 'with' block (None if no exception).
            exc_val: The exception instance raised (None if no exception).
            exc_tb: A traceback object (None if no exception).
        """
        if self.cursor:
            logging.info("Closing database cursor.")
            self.cursor.close()
        if self.conn:
            logging.info("Closing database connection.")
            self.conn.close()
        
        # If an exception occurred within the 'with' block, log it.
        # Returning False (or None, which is default) from __exit__ will propagate the exception.
        # Returning True would suppress the exception.
        if exc_type:
            logging.error(f"An exception occurred inside the 'with' block: {exc_val}", exc_info=True)
        return False 

# --- Main execution block for demonstrating usage ---
if __name__ == "__main__":
    db_file = 'users.db'
    setup_db(db_file) # Ensure the database is set up with 'age' data

    print("\n--- Test Case 1: Select users older than 25 (with parameters) ---")
    query_age = "SELECT name, age FROM users WHERE age > ?"
    param_age = (25,) # Parameters must be an iterable (tuple or list), even for a single parameter
    try:
        # Use the ExecuteQuery context manager
        with ExecuteQuery(db_file, query_age, param_age) as users_older_than_25:
            print(f"Users older than {param_age[0]}:")
            if users_older_than_25:
                for user in users_older_than_25:
                    print(user)
            else:
                print("No users found matching the criteria.")
        print("--> Test Case 1 completed successfully and connection closed (check logs above).")
    except Exception as e:
        print(f"An error occurred in Test Case 1: {type(e).__name__}: {e}")

    print("\n--- Test Case 2: Select all users (no parameters) ---")
    query_all = "SELECT * FROM users"
    try:
        with ExecuteQuery(db_file, query_all) as all_users:
            print("All users in the database:")
            if all_users:
                for user in all_users:
                    print(user)
            else:
                print("No users found.")
        print("--> Test Case 2 completed successfully and connection closed (check logs above).")
    except Exception as e:
        print(f"An error occurred in Test Case 2: {type(e).__name__}: {e}")

    print("\n--- Test Case 3: Simulate an invalid query (error handling) ---")
    invalid_query = "SELECT * FROM non_existent_table"
    try:
        with ExecuteQuery(db_file, invalid_query) as result_error:
            # This line should not be reached if an error occurs and is propagated
            print("This line should not be reached if an error occurs.")
            print("Result of invalid query:", result_error)
        print("--> This line should not be printed if error propagates correctly.")
    except sqlite3.OperationalError as e:
        print(f"Caught expected error for invalid query: {e}")
        print("--> Connection correctly closed by context manager (check logs above).")
    except Exception as e:
        print(f"Caught unexpected error type in Test Case 3: {type(e).__name__}: {e}")

    print("\n--- Test Case 4: Query with wrong number of parameters (error handling) ---")
    query_wrong_params = "SELECT name FROM users WHERE id = ?"
    wrong_params = (1, 2) # Expected 1 parameter, but 2 are given
    try:
        with ExecuteQuery(db_file, query_wrong_params, wrong_params) as result_wrong:
            print("This line should not be reached.")
            print(result_wrong)
        print("--> Connection should be closed.")
    except sqlite3.ProgrammingError as e:
        print(f"Caught expected error for wrong parameters: {e}")
        print("--> Connection correctly closed by context manager (check logs above).")
    except Exception as e:
        print(f"Caught unexpected error type in Test Case 4: {type(e).__name__}: {e}")
