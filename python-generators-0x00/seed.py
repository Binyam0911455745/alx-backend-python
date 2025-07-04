import mysql.connector
import csv
import os
from uuid import UUID

# Database configuration
# Recommended: Set these as environment variables for security in production.
# Example: export MYSQL_HOST="localhost"
#          export MYSQL_USER="root"
#          export MYSQL_PASSWORD="your_mysql_password"
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'Bin@0911455745'), # Replace with your MySQL password
    'database': 'ALX_prodev'
}

def connect_db():
    """
    Connects to the MySQL database server (without specifying a database).
    Returns the connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
    return None

def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    """
    if not connection or not connection.is_connected():
        print("Error: No active database connection to create database.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        connection.commit()
        print(f"Database {DB_CONFIG['database']} created or already exists.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    Returns the connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        if connection.is_connected():
            print(f"Successfully connected to database {DB_CONFIG['database']}.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to {DB_CONFIG['database']} database: {err}")
    return None

def create_table(connection):
    """
    Creates a table user_data if it does not exists with the required fields.
    """
    if not connection or not connection.is_connected():
        print("Error: No active database connection to create table.")
        return

    try:
        cursor = connection.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY, -- UUIDs are typically stored as VARCHAR(36)
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(10, 2) NOT NULL,
            INDEX(user_id) -- Explicitly indexing as requested, though PRIMARY KEY implies it.
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created successfully.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

def insert_data(connection, csv_file_path):
    """
    Inserts data from a CSV file into the user_data table.
    Uses INSERT IGNORE to skip rows with duplicate primary keys (user_id).
    Assumes CSV format: user_id,name,email,age (header row required).
    """
    if not connection or not connection.is_connected():
        print("Error: No active database connection to insert data.")
        return
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return

    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT IGNORE INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        
        inserted_rows_count = 0
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader) # Skip header row

            # Determine column indices dynamically from CSV header
            try:
                user_id_idx = header.index('user_id')
                name_idx = header.index('name')
                email_idx = header.index('email')
                age_idx = header.index('age')
            except ValueError as e:
                print(f"Error: CSV header is missing an expected column: {e}")
                return

            for row in reader:
                if not row: # Skip empty rows
                    continue
                try:
                    # Validate UUID format
                    user_id = row[user_id_idx]
                    try:
                        UUID(user_id) # Validate if it's a valid UUID string
                    except ValueError:
                        print(f"Skipping row with invalid user_id UUID format: '{user_id}'")
                        continue

                    name = row[name_idx]
                    email = row[email_idx]
                    
                    # Convert age to float for DECIMAL type, handle potential errors
                    try:
                        age = float(row[age_idx])
                    except ValueError:
                        print(f"Skipping row with invalid age format: '{row[age_idx]}'")
                        continue

                    cursor.execute(insert_query, (user_id, name, email, age))
                    inserted_rows_count += cursor.rowcount # rowcount is 1 for insert, 0 for ignore
                except IndexError:
                    print(f"Skipping malformed row (too few columns): {row}")
                    continue
                except mysql.connector.Error as insert_err:
                    # Error code 1062 is for duplicate entry for primary key/unique key
                    if insert_err.errno == 1062:
                        print(f"Skipping duplicate row (user_id already exists): {row}")
                    else:
                        print(f"Error inserting row {row}: {insert_err}")
                    continue # Continue to next row even if one fails
        
        connection.commit()
        print(f"Data insertion process complete. {inserted_rows_count} new unique rows inserted (duplicates ignored).")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error during data insertion: {err}")


def stream_data(connection):
    """
    Generator function that streams rows from the user_data table one by one.
    Yields each row as a tuple.
    Ensures the cursor is closed even if iteration is incomplete.
    """
    if not connection or not connection.is_connected():
        print("Error: No active database connection to stream data.")
        return

    cursor = None
    try:
        # Using buffered=True for demonstration simplicity.
        # For truly massive datasets that exceed client memory,
        # consider mysql.connector.cursor.MySQLCursorUnbuffered for true streaming.
        cursor = connection.cursor(buffered=True)
        
        cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id;")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break # No more rows
            yield row # This is where the generator yields one row at a time
    except mysql.connector.Error as err:
        print(f"Error streaming data: {err}")
    finally:
        if cursor:
            cursor.close()

# This __main__ block is primarily for testing seed.py directly.
# The 0-main.py script will import and use these functions.
if __name__ == '__main__':
    print("--- Running seed.py directly for demonstration ---")
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close() # Close initial connection to the server

        conn_prodev = connect_to_prodev() # Connect directly to ALX_prodev database
        if conn_prodev:
            create_table(conn_prodev)
            
            # Ensure 'user_data.csv' exists in the same directory!
            insert_data(conn_prodev, 'user_data.csv')

            # Demonstrate data retrieval using fetchall (non-generator)
            cursor = conn_prodev.cursor()
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{DB_CONFIG['database']}';")
            result = cursor.fetchone()
            if result:
                print(f"Database {DB_CONFIG['database']} is present ")
            cursor.execute(f"SELECT * FROM user_data LIMIT 5;")
            rows = cursor.fetchall()
            print("\nFirst 5 rows fetched using fetchall():")
            print(rows)
            cursor.close()

            # Demonstrate streaming data using the stream_data generator
            print("\n--- Streaming data using stream_data generator ---")
            streamed_count = 0
            for row in stream_data(conn_prodev):
                print(f"Streamed row: {row}")
                streamed_count += 1
                if streamed_count >= 10: # Limit for demonstration purposes
                    print("... (showing first 10 rows from stream, if available)")
                    break
            
            conn_prodev.close()
            print("\nDatabase connection closed.")
        else:
            print("Failed to connect to ALX_prodev database.")
    else:
        print("Failed to connect to MySQL server initially.")
