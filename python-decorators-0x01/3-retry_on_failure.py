import time
import sqlite3
import functools
import logging
import sys

# Configure basic logging to stdout for clarity and debugging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Copy `with_db_connection` from Task 1 (or 2) here ---
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
            logging.info("Opening database connection...")
            conn = sqlite3.connect('users.db')
            
            # Pass the connection as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            
            return result
        except sqlite3.Error as e:
            logging.error(f"Database error during execution of '{func.__name__}': {e}", exc_info=True)
            raise # Re-raise the exception after logging
        except Exception as e:
            logging.error(f"An unexpected error occurred during execution of '{func.__name__}': {e}", exc_info=True)
            raise # Re-raise the exception
        finally:
            # Ensure the connection is closed even if an error occurred
            if conn:
                logging.info("Closing database connection.")
                conn.close()
    return wrapper

# --- Implement `retry_on_failure` decorator here for Task 3 ---
def retry_on_failure(retries=3, delay=2):
    """
    A decorator factory that retries the decorated function a specified number of times
    if it raises an exception. It waits for a delay between retries.

    Args:
        retries (int): The maximum number of times to retry the function
                       (e.g., if retries=3, it will attempt 1 initial + 3 retries = 4 attempts total).
        delay (int): The delay in seconds between retries.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries + 1): # +1 includes the initial attempt
                try:
                    if attempt > 0:
                        logging.info(f"Attempt {attempt}/{retries}: Retrying '{func.__name__}' after {delay}s delay...")
                    else:
                        logging.info(f"Attempt {attempt}/{retries}: Initial call to '{func.__name__}'...")
                    
                    return func(*args, **kwargs) # Try to execute the wrapped function
                except Exception as e:
                    logging.warning(f"Attempt {attempt}/{retries}: Call to '{func.__name__}' failed with error: {e}")
                    if attempt == retries: # If this was the last allowed attempt
                        logging.error(f"'{func.__name__}' failed after {retries} retries. Re-raising final exception.")
                        raise # Re-raise the last exception
                    time.sleep(delay) # Wait before the next retry
            # This line should ideally not be reached, as either the function returns or an exception is re-raised.
            raise RuntimeError(f"Unexpected state: '{func.__name__}' did not return or raise after all retries.")
        return wrapper
    return decorator

# --- Helper function to set up the SQLite database for testing ---
def setup_db():
    """
    Sets up a simple SQLite 'users.db' database with a 'users' table
    and inserts some sample data if the table is empty.
    """
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            try:
                cursor.execute("INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com')")
                cursor.execute("INSERT INTO users (name, email) VALUES ('Bob Williams', 'bob@example.com')")
                conn.commit()
                logging.info("Sample data inserted into 'users' table during setup.")
            except sqlite3.IntegrityError:
                logging.info("Sample data already exists during setup (email unique constraint violated).")
        else:
            logging.info("Users table already contains data, skipping sample insertion during setup.")
            
    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Provided example function for Task 3 with retry simulation ---

# Global counter to simulate transient failures for testing purposes
# This variable will be modified by fetch_users_with_retry to control when it fails.
_simulate_failure_count = 0
_MAX_FAILURES_BEFORE_SUCCESS = 2 # The function will fail 2 times, and succeed on the 3rd attempt.

@with_db_connection
@retry_on_failure(retries=3, delay=1) # Parameters from task description: retries=3, delay=1
def fetch_users_with_retry(conn):
    """
    Attempts to fetch users. Designed to simulate transient failures for testing.
    This function will raise an error a few times before succeeding based on `_simulate_failure_count`.
    """
    global _simulate_failure_count
    _simulate_failure_count += 1
    
    # Simulate a transient database error for the first `_MAX_FAILURES_BEFORE_SUCCESS` calls
    if _simulate_failure_count <= _MAX_FAILURES_BEFORE_SUCCESS:
        logging.warning(f"Simulating a transient error on call {_simulate_failure_count} of fetch_users_with_retry...")
        # Raising a common database error for realism, but it could be any Exception.
        raise sqlite3.OperationalError("Database connection temporarily unavailable (simulated transient error).")
    
    logging.info(f"Successfully executing query on call {_simulate_failure_count}.")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# --- Main execution block ---
if __name__ == "__main__":
    setup_db() # Ensure database is ready

    # Test Case 1: Function succeeds after some retries
    print("\n--- Test Case 1: Fetch users, expecting success after retries ---")
    _simulate_failure_count = 0 # Reset counter for this test
    _MAX_FAILURES_BEFORE_SUCCESS = 2 # Fail 2 times, succeed on 3rd attempt (attempt 2 in 0-indexed loop of decorator)
    try:
        users = fetch_users_with_retry()
        print(f"SUCCESS: Successfully fetched {len(users)} users after retries.")
        print("Users:", users)
    except Exception as e:
        print(f"FAILURE: Failed to fetch users after retries unexpectedly: {type(e).__name__}: {e}")
    
    # Test Case 2: Function always fails, expecting a final exception after all retries are exhausted
    print("\n--- Test Case 2: Fetch users, expecting failure after all retries ---")
    _simulate_failure_count = 0 # Reset counter for this test
    # Set MAX_FAILURES_BEFORE_SUCCESS higher than decorator's `retries` (3) to ensure it always fails.
    _MAX_FAILURES_BEFORE_SUCCESS = 5 
    try:
        users = fetch_users_with_retry()
        print(f"FAILURE: Unexpectedly fetched users: {len(users)} users. Expected failure.")
    except sqlite3.OperationalError as e:
        print(f"SUCCESS: Correctly failed after all retries: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"FAILURE: Failed with unexpected error type: {type(e).__name__}: {e}")
    finally:
        # Reset the failure simulation for future runs/tests
        _simulate_failure_count = 0 
        _MAX_FAILURES_BEFORE_SUCCESS = 2 # Reset to default for typical operation

    # Test Case 3: Function succeeds on the first attempt (no retries needed)
    print("\n--- Test Case 3: Fetch users, expecting success on first attempt ---")
    _simulate_failure_count = 99 # Make it always succeed by making call_count > _MAX_FAILURES_BEFORE_SUCCESS immediately
    try:
        users = fetch_users_with_retry()
        print(f"SUCCESS: Successfully fetched {len(users)} users on first attempt (no retries).")
        print("Users:", users)
    except Exception as e:
        print(f"FAILURE: Failed unexpectedly on first attempt test: {type(e).__name__}: {e}")
