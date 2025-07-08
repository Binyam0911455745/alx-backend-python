import time
import sqlite3
import functools
import logging
import sys

# Configure basic logging to stdout for clarity and debugging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Copy `with_db_connection` from a previous task ---
# This remains the same.
def with_db_connection(func):
    """
    A decorator that automatically opens a SQLite database connection ('users.db'),
    passes it as the first argument (conn) to the decorated function,
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
            raise 
        except Exception as e:
            logging.error(f"An unexpected error occurred during execution of '{func.__name__}': {e}", exc_info=True)
            raise 
        finally:
            if conn:
                logging.info("Closing database connection.")
                conn.close()
    return wrapper

# --- Global cache for queries ---
query_cache = {}

# --- Implement `cache_query` decorator (Adjusted for outer position) ---
def cache_query(func):
    """
    A decorator that caches the results of a database query based on the SQL query string.
    If the query is in the cache, the cached result is returned immediately.
    Otherwise, the query is executed (by the decorated function), its result is cached, and then returned.

    Assumes the decorated function's actual *query string* will be passed as the 
    first positional argument (if no other leading args are present) 
    or as a keyword argument named 'query'. This is because 'conn' 
    will be provided *after* this decorator by @with_db_connection.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine the cache key (the SQL query string)
        query = None
        
        # When @cache_query is outermost, 'conn' is NOT yet in args.
        # So the 'query' is either args[0] or kwargs['query'].
        if args and isinstance(args[0], str): 
            query = args[0]
        if 'query' in kwargs: # Kwarg takes precedence
            query = kwargs['query']

        if not query:
            logging.error(f"Could not identify SQL query for caching in '{func.__name__}'. "
                          f"Expected query as first positional arg or 'query' keyword arg. "
                          f"Args: {args}, Kwargs: {kwargs}")
            # If we can't find a query, execute without caching to avoid breaking the function.
            return func(*args, **kwargs) # Pass args/kwargs as received by cache_query wrapper

        # Check if the query result is already in the cache
        if query in query_cache:
            logging.info(f"Retrieving result for query '{query}' from cache.")
            return query_cache[query]
        
        # If not in cache, execute the original function to get the result.
        # The original func here is the 'wrapper' from @with_db_connection,
        # which will then provide the 'conn' object.
        logging.info(f"Executing query '{query}' and caching its result.")
        result = func(*args, **kwargs) # Pass args/kwargs as received by cache_query wrapper
        
        # Store the result in the cache
        query_cache[query] = result
        
        return result
    return wrapper

# --- Helper function to set up the SQLite database for testing ---
# This remains the same.
def setup_db():
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

# --- Provided example function for Task 4 (WITH REVERSED DECORATOR ORDER) ---

# Apply @cache_query first (outermost)
@cache_query
# Then apply @with_db_connection (innermost, just above the function definition)
@with_db_connection
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database using the provided query.
    Results will be cached by the @cache_query decorator.
    """
    # This line only executes if @cache_query results in a cache miss
    logging.info(f"Executing actual database query: '{query}'") 
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# --- Main execution block for testing ---
if __name__ == "__main__":
    setup_db() # Ensure database is ready

    # Clear cache for a clean test run (important for repeat executions of script)
    query_cache.clear() 
    print("--- Cache cleared for new test run ---")

    # First call will execute the query and cache the result
    print("\n--- First call: 'SELECT * FROM users' (expected database execution) ---")
    start_time = time.time()
    users = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Users fetched (first call): {len(users)} users.")
    print(f"Time taken: {end_time - start_time:.4f} seconds.")
    print("Cached queries:", list(query_cache.keys()))


    # Second call will use the cached result (expected cache hit, NO DB CONNECTION OPEN/CLOSE)
    print("\n--- Second call: 'SELECT * FROM users' (expected cache hit) ---")
    start_time = time.time()
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Users fetched (second call): {len(users_again)} users.")
    print(f"Time taken: {end_time - start_time:.4f} seconds.")
    assert users == users_again
    print("Verification: Results from first and second call are identical.")


    # Third call with a different query (expected database execution and new cache entry)
    print("\n--- Third call: 'SELECT name FROM users WHERE id = 1' (expected database execution) ---")
    start_time = time.time()
    user_name_1 = fetch_users_with_cache(query="SELECT name FROM users WHERE id = 1")
    end_time = time.time()
    print(f"User name fetched (third call): {user_name_1}")
    print(f"Time taken: {end_time - start_time:.4f} seconds.")
    print("Cached queries:", list(query_cache.keys()))


    # Fourth call, repeating the third query (expected cache hit)
    print("\n--- Fourth call: 'SELECT name FROM users WHERE id = 1' (expected cache hit) ---")
    start_time = time.time()
    user_name_1_again = fetch_users_with_cache(query="SELECT name FROM users WHERE id = 1")
    end_time = time.time()
    print(f"User name fetched (fourth call): {user_name_1_again}")
    print(f"Time taken: {end_time - start_time:.4f} seconds.")
    assert user_name_1 == user_name_1_again
    print("Verification: Results from third and fourth call are identical.")
    print("Cached queries:", list(query_cache.keys()))

    # Test with positional argument for query (should now work correctly)
    print("\n--- Fifth call: Positional query 'SELECT email FROM users WHERE id = 2' (expected database execution) ---")
    start_time = time.time()
    # Now, 'query' is the *first* argument passed to the outermost decorator
    user_email_2 = fetch_users_with_cache("SELECT email FROM users WHERE id = 2") 
    end_time = time.time()
    print(f"User email fetched (fifth call): {user_email_2}")
    print(f"Time taken: {end_time - start_time:.4f} seconds.")
    print("Cached queries:", list(query_cache.keys()))
    
    print("\n--- Sixth call: Positional query 'SELECT email FROM users WHERE id = 2' (expected cache hit) ---")
    start_time = time.time()
    user_email_2_again = fetch_users_with_cache("SELECT email FROM users WHERE id = 2")
    end_time = time.time()
    print(f"User email fetched (sixth call): {user_email_2_again}")
    print(f"Time taken: {end_time - start_time:.4f} seconds.")
    assert user_email_2 == user_email_2_again
    print("Verification: Results from fifth and sixth call are identical.")
    print("Cached queries:", list(query_cache.keys()))

