import asyncio
import aiosqlite
import logging
import sys
import time
import sqlite3 # Import standard sqlite3 for the synchronous setup_db function

# Configure basic logging to stdout for clarity and debugging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper function to set up the SQLite database (adapted from previous tasks) ---
def setup_db(db_name='users.db'):
    """
    Sets up a simple SQLite database by ensuring the 'users' table exists
    with 'id', 'name', 'email', and 'age' columns, and populates it with sample data.
    It drops the table if it exists to ensure a clean schema for testing.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Drop the table if it exists to ensure a clean schema for testing
        logging.info("Dropping existing 'users' table if it exists to ensure fresh schema.")
        cursor.execute('DROP TABLE IF EXISTS users')
        conn.commit()

        # Create users table with all necessary columns, including 'age'
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER
            )
        ''')
        conn.commit()
        logging.info("Created 'users' table with 'id', 'name', 'email', 'age' columns.")

        # Sample data including ages, ensuring some users are older than 40
        users_to_insert = [
            ('Alice Johnson', 'alice@example.com', 30),
            ('Bob Williams', 'bob@example.com', 22),
            ('Charlie Brown', 'charlie@example.com', 45), # Older user
            ('David Lee', 'david.lee@example.com', 28),
            ('Eve Davis', 'eve@example.com', 50),       # Older user
            ('Frank Green', 'frank@example.com', 20),
            ('Grace Hall', 'grace@example.com', 42)    # Older user
        ]

        inserted_count = 0
        for name, email, age in users_to_insert:
            try:
                cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (name, email, age))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # This should ideally not happen after dropping the table, but good for robustness
                logging.warning(f"Skipping insert for {name} ({email}) due to unique email constraint.")
        conn.commit()
        logging.info(f"Inserted {inserted_count} sample users into 'users' table.")

    except sqlite3.Error as e:
        logging.error(f"Error setting up database: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# --- Asynchronous functions for fetching data ---

# CHANGE START: Removed db_name='users.db' from signature
async def async_fetch_users():
    """
    Asynchronously fetches all users from the database.
    Uses aiosqlite for asynchronous database operations.
    """
    db_name = 'users.db' # Define db_name inside the function
    logging.info("async_fetch_users: Starting to fetch all users.")
    start_time = time.time()
    results = []
    try:
        # Use aiosqlite's async context manager for connection and cursor
        async with aiosqlite.connect(db_name) as db:
            # Simulate a brief delay to make concurrency more observable
            await asyncio.sleep(0.1)
            async with db.cursor() as cursor:
                await cursor.execute("SELECT id, name, email, age FROM users")
                results = await cursor.fetchall()
        logging.info(f"async_fetch_users: Finished fetching all users in {time.time() - start_time:.4f} seconds.")
    except Exception as e:
        logging.error(f"async_fetch_users: An error occurred: {e}", exc_info=True)
    return results

# CHANGE START: Removed db_name='users.db' from signature
async def async_fetch_older_users():
    """
    Asynchronously fetches users older than 40 from the database.
    Uses aiosqlite for asynchronous database operations.
    """
    db_name = 'users.db' # Define db_name inside the function
    logging.info("async_fetch_older_users: Starting to fetch older users.")
    start_time = time.time()
    results = []
    try:
        async with aiosqlite.connect(db_name) as db:
            # Simulate a brief delay to make concurrency more observable
            await asyncio.sleep(0.1)
            async with db.cursor() as cursor:
                await cursor.execute("SELECT id, name, email, age FROM users WHERE age > ?", (40,))
                results = await cursor.fetchall()
        logging.info(f"async_fetch_older_users: Finished fetching older users in {time.time() - start_time:.4f} seconds.")
    except Exception as e:
        logging.error(f"async_fetch_older_users: An error occurred: {e}", exc_info=True)
    return results

# --- Main asynchronous function to run queries concurrently ---
async def fetch_concurrently():
    """
    Executes multiple asynchronous database queries concurrently using asyncio.gather.
    """
    logging.info("fetch_concurrently: Starting concurrent fetching operations.")
    total_start_time = time.time()

    # Use asyncio.gather to run both fetch operations concurrently.
    # asyncio.gather takes coroutine objects (results of calling async functions).
    # It waits for all of them to complete and returns their results in the order
    # they were passed.

    all_users_result, older_users_result = await asyncio.gather(
        async_fetch_users(),       # Call the async function to get a coroutine
        async_fetch_older_users()  # Call the async function to get a coroutine
    )

    total_end_time = time.time()
    logging.info(f"fetch_concurrently: All concurrent fetches completed in {total_end_time - total_start_time:.4f} seconds.")

    print("\n--- Results from Concurrent Queries ---")

    print("\nAll Users:")
    if all_users_result:
        for user in all_users_result:
            print(user)
    else:
        print("No users found.")

    print("\nUsers Older Than 40:")
    if older_users_result:
        for user in older_users_result:
            print(user)
    else:
        print("No users older than 40 found.")

# --- Main execution block ---
if __name__ == "__main__":
    db_file = 'users.db'

    print("--- Setting up database ---")
    setup_db(db_file) # Synchronous setup for database preparation
    print("--- Database setup complete ---")

    print("\n--- Running concurrent fetch operations ---")
    # asyncio.run() is the entry point for running the top-level async function
    asyncio.run(fetch_concurrently())
    print("--- Concurrent fetch operations finished ---")
