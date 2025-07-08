import sqlite3
import functools
import logging
import sys

# Configure basic logging to stdout for clarity and debugging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. Copy `with_db_connection` from Task 1 ---
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
            # The decorated function must accept 'conn' as its first parameter.
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

# --- 2. Implement the `transactional` decorator for Task 2 ---
def transactional(func):
    """
    A decorator that manages database transactions.
    It expects the decorated function to receive a database connection 'conn'
    as its first argument (usually provided by @with_db_connection).

    If the decorated function executes successfully, the transaction is committed.
    If the function raises any Exception, the transaction is rolled back.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # The 'conn' object is expected to be the first positional argument.
        # This is because @with_db_connection (which is applied first)
        # provides the connection as the first argument to the function it wraps.
        if not args or not isinstance(args[0], sqlite3.Connection):
            logging.error(f"Error: Function '{func.__name__}' decorated with @transactional "
                          f"did not receive a sqlite3.Connection object as its first argument.")
            raise TypeError("Expected database connection as the first argument for transactional decorator.")
        
        conn = args[0] # Get the connection object from the function's arguments

        try:
            logging.info(f"Starting transaction for '{func.__name__}'...")
            result = func(*args, **kwargs) # Execute the decorated function
            conn.commit() # Commit changes if function completes without error
            logging.info(f"Transaction committed for '{func.__name__}'.")
            return result
        except Exception as e:
            conn.rollback() # Rollback changes if any error occurs
            logging.error(f"Error in '{func.__name__}'. Transaction rolled back: {e}", exc_info=True)
            raise # Re-raise the exception to propagate the error
    return wrapper

# --- Helper function to set up the SQLite database for testing ---
# (Copied and slightly adjusted from previous tasks for robust testing)
def setup_db():
    conn = None
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

        # Insert some dummy data if the table is empty or has less than 2 users
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count < 2: # Ensure at least two users for robust testing
            try:
                cursor.execute("INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com')")
                cursor.execute("INSERT INTO users (name, email) VALUES ('Bob Williams', 'bob@example.com')")
                conn.commit()
                logging.info("Sample data inserted into 'users' table during setup.")
            except sqlite3.IntegrityError:
                logging.info("Sample data already exists (email unique constraint violated) during setup.")
            except Exception as e:
                logging.error(f"Error inserting sample data during setup: {e}", exc_info=True)
        else:
            logging.info("Users table already contains data, skipping sample insertion during setup.")
            
    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Provided example function for Task 2 ---
@with_db_connection  # This provides the 'conn' object
@transactional       # This manages the transaction (commit/rollback)
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email in the database.
    This function expects a connection object 'conn' as its first argument.
    """
    logging.info(f"Attempting to update user ID {user_id} email to {new_email}...")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    logging.info(f"Update SQL executed for user ID {user_id}.") # This happens before commit/rollback by @transactional

# --- Additional functions for testing the transactional decorator ---

@with_db_connection
@transactional
def create_user(conn, name, email):
    """
    Creates a new user. Will fail if email is not unique (due to UNIQUE constraint on 'email').
    """
    logging.info(f"Attempting to insert new user: Name='{name}', Email='{email}'")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    logging.info(f"Insert SQL executed for user: {name}.")

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Helper function to retrieve user data for verification (does not commit/rollback itself).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

@with_db_connection
def get_all_users(conn):
    """
    Helper function to retrieve all users for verification.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# --- Main execution block for testing ---
if __name__ == "__main__":
    setup_db() # Ensure database is ready and has initial data

    # Test Case 1: Successful Email Update
    print("\n--- Test Case 1: Successful Email Update ---")
    initial_user_1 = get_user_by_id(user_id=1)
    print(f"User 1 initial state: {initial_user_1}")
    new_email_success = 'john.doe@example.com'
    try:
        update_user_email(user_id=1, new_email=new_email_success)
        updated_user_1 = get_user_by_id(user_id=1)
        print(f"User 1 after successful update: {updated_user_1}")
        assert updated_user_1[2] == new_email_success
        print("SUCCESS: User 1 email updated and committed.")
    except Exception as e:
        print(f"FAILURE: Test 1 failed unexpectedly: {e}")

    # Test Case 2: Rollback on Error (Duplicate Email Violation)
    print("\n--- Test Case 2: Rollback on Error (Duplicate Email) ---")
    # Get user 2's email to use as a duplicate
    user_2_info = get_user_by_id(user_id=2)
    if user_2_info:
        duplicate_email = user_2_info[2] # e.g., 'bob@example.com'
    else:
        print("Skipping Test 2: User 2 not found in DB.")
        duplicate_email = "some_non_unique@example.com" # Fallback
    
    user_1_initial_email = get_user_by_id(user_id=1)[2] # Get Alice's current email
    print(f"User 1 current email: {user_1_initial_email}")
    print(f"Attempting to update User 1's email to a duplicate: {duplicate_email}")
    try:
        # This will attempt to update user 1's email to user 2's, violating UNIQUE constraint
        update_user_email(user_id=1, new_email=duplicate_email)
        print("FAILURE: Test 2 failed - Expected an error but transaction was committed.")
    except sqlite3.IntegrityError as e:
        print(f"SUCCESS: Caught expected IntegrityError: {e}")
        # Verify rollback: user 1's email should be original
        user_1_after_rollback = get_user_by_id(user_id=1)
        print(f"User 1 after rollback attempt: {user_1_after_rollback}")
        assert user_1_after_rollback[2] == user_1_initial_email
        print("Rollback confirmed: User 1's email reverted to original.")
    except Exception as e:
        print(f"FAILURE: Test 2 failed with unexpected error: {e}")

    # Test Case 3: Successful User Creation
    print("\n--- Test Case 3: Successful User Creation ---")
    new_user_name = "David Lee"
    new_user_email = "david.lee@example.com"
    initial_user_count = len(get_all_users())
    print(f"Initial user count: {initial_user_count}")
    try:
        create_user(name=new_user_name, email=new_user_email)
        final_user_count = len(get_all_users())
        print(f"Final user count: {final_user_count}")
        assert final_user_count == initial_user_count + 1
        print("SUCCESS: New user created and committed.")
        print("All users after creation:", get_all_users())
    except Exception as e:
        print(f"FAILURE: Test 3 failed unexpectedly: {e}")

    # Test Case 4: Rollback on Duplicate User Creation
    print("\n--- Test Case 4: Rollback on Duplicate User Creation ---")
    duplicate_user_name = "Frank Green"
    # Use an email that already exists (e.g., Alice's email)
    duplicate_user_email = "alice@example.com" 
    initial_user_count_2 = len(get_all_users())
    print(f"Initial user count: {initial_user_count_2}")
    try:
        create_user(name=duplicate_user_name, email=duplicate_user_email)
        print("FAILURE: Test 4 failed - Expected an error but transaction was committed.")
    except sqlite3.IntegrityError as e:
        print(f"SUCCESS: Caught expected IntegrityError: {e}")
        # Verify rollback: user count should be same as before attempt
        final_user_count_2 = len(get_all_users())
        print(f"Final user count: {final_user_count_2}")
        assert final_user_count_2 == initial_user_count_2
        print("Rollback confirmed: User creation was rolled back.")
    except Exception as e:
        print(f"FAILURE: Test 4 failed with unexpected error: {e}")
