## Prerequisites

Before running the scripts and queries, ensure you have the following installed:

* **MySQL Server:** A running MySQL database instance.
* **Python 3:** Version 3.8 or higher is recommended.
* **`mysql-connector-python`:** Python library for connecting to MySQL. Install it using pip:
    ```bash
    pip install mysql-connector-python
    ```

## Database Schemas Used

This project utilizes two distinct database contexts:

### 1. `ALX_prodev` Database (for `seed.py` and `0-main.py`)

* **Purpose:** Used for demonstrating basic database setup, CSV data insertion, and Python data streaming using generators.
* **Database Name:** `ALX_prodev`
* **Table:** `user_data`
    * `user_id` (VARCHAR(36) PRIMARY KEY, Indexed) - Stores UUIDs for unique user identification.
    * `name` (VARCHAR(255) NOT NULL)
    * `email` (VARCHAR(255) NOT NULL)
    * `age` (DECIMAL(10, 2) NOT NULL)

### 2. `alx_airbnb_database` Database (for `joins_queries.sql`)

* **Purpose:** Used for demonstrating complex SQL join operations on a hypothetical Airbnb-like data model.
* **Database Name:** `alx_airbnb_database`
* **Assumed Tables:**
    * **`users`**:
        * `user_id` (PRIMARY KEY)
        * `username` (VARCHAR)
        * `email` (VARCHAR)
    * **`properties`**:
        * `property_id` (PRIMARY KEY)
        * `name` (VARCHAR) - Property name (e.g., "Cozy Apartment")
        * `city` (VARCHAR)
        * `owner_id` (FOREIGN KEY to `users.user_id`)
    * **`bookings`**:
        * `booking_id` (PRIMARY KEY)
        * `user_id` (FOREIGN KEY to `users.user_id`) - The user who made the booking
        * `property_id` (FOREIGN KEY to `properties.property_id`) - The property booked
        * `start_date` (DATE)
        * `end_date` (DATE)
    * **`reviews`**:
        * `review_id` (PRIMARY KEY)
        * `property_id` (FOREIGN KEY to `properties.property_id`) - The property being reviewed
        * `user_id` (FOREIGN KEY to `users.user_id`) - The user who wrote the review
        * `rating` (INT) - e.g., 1-5
        * `comment` (TEXT)

---

## Task 1: Database Setup, Data Insertion & Python Generators

**Objective:** Create a generator that streams rows from an SQL database one by one, demonstrating efficient data retrieval.

### `seed.py` Prototypes:

* `def connect_db():` - Connects to the MySQL database server.
* `def create_database(connection):` - Creates the database `ALX_prodev` if it does not exist.
* `def connect_to_prodev():` - Connects to the `ALX_prodev` database in MySQL.
* `def create_table(connection):` - Creates the `user_data` table if it does not exist with the required fields.
* `def insert_data(connection, csv_file_path):` - Inserts data from the specified CSV file into the database using `INSERT IGNORE` to handle potential duplicates.
* `def stream_data(connection):` - **The generator function** that streams rows from the `user_data` table one by one. It yields each row as a tuple, optimizing memory usage for large datasets.

### Setup and Running:

1.  **Create `database-adv-script` Directory:** Ensure you are in the `alx-airbnb-database` repository root and create the `database-adv-script` directory.
    ```bash
    mkdir -p database-adv-script
    cd database-adv-script
    ```

2.  **Create `seed.py`:**
    Place the complete `seed.py` code (as provided in previous solutions, including `DB_CONFIG` and all prototypes) into `database-adv-script/seed.py`.
    **Important:** Update the `password` in `DB_CONFIG` to your actual MySQL root password, or set it via environment variables (e.g., `export MYSQL_PASSWORD="your_password"`).

3.  **Create `user_data.csv`:**
    Create a file named `user_data.csv` in the `database-adv-script` directory with the following content:
    ```csv
    user_id,name,email,age
    00000000-0000-0000-0000-000000000001,Alice Johnson,alice.j@example.com,28.5
    00000000-0000-0000-0000-000000000002,Bob Williams,bob.w@example.com,45
    00000000-0000-0000-0000-000000000003,Charlie Brown,charlie.b@example.com,22.0
    00000000-0000-0000-0000-000000000004,Diana Miller,diana.m@example.com,37
    00000000-0000-0000-0000-000000000005,Ethan Davis,ethan.d@example.com,51.75
    00000000-0000-0000-0000-000000000006,Fiona Garcia,fiona.g@example.com,29
    00000000-0000-0000-0000-000000000007,George Wilson,george.w@example.com,60
    00000000-0000-0000-0000-000000000008,Hannah Green,hannah.g@example.com,33.3
    00000000-0000-0000-0000-000000000009,Ivy King,ivy.k@example.com,41
    00000000-0000-0000-0000-000000000010,Jack Lee,jack.l@example.com,27
    00000000-0000-0000-0000-000000000011,Karen Scott,karen.s@example.com,39.9
    00000000-0000-0000-0000-000000000012,Liam Hall,liam.h@example.com,50
    ```

4.  **Create `0-main.py`:**
    Place the complete `0-main.py` code (which imports `seed` and calls its functions, including consuming `stream_data`) into `database-adv-script/0-main.py`.
    ```python
    #!/usr/bin/python3

    seed = __import__('seed')

    print("--- Starting database setup and data operations ---")

    connection = seed.connect_db()
    if connection:
        seed.create_database(connection)
        connection.close()
        print(f"Initial connection successful. Database checked/created.")

        connection_to_prodev = seed.connect_to_prodev()

        if connection_to_prodev:
            seed.create_table(connection_to_prodev)
            seed.insert_data(connection_to_prodev, 'user_data.csv')

            cursor = connection_to_prodev.cursor()
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{seed.DB_CONFIG['database']}';")
            result = cursor.fetchone()
            if result:
                print(f"\nVerification: Database '{seed.DB_CONFIG['database']}' is confirmed to exist.")
            
            cursor.execute(f"SELECT COUNT(*) FROM user_data;")
            count = cursor.fetchone()[0]
            print(f"Verification: Total rows in user_data table: {count}")

            cursor.execute(f"SELECT user_id, name, email, age FROM user_data LIMIT 5;")
            rows = cursor.fetchall()
            print("\n--- First 5 rows fetched using fetchall() (all at once) ---")
            for row in rows:
                print(row)
            cursor.close()

            print("\n--- Streaming data using seed.stream_data generator (one by one) ---")
            streamed_count = 0
            for row in seed.stream_data(connection_to_prodev):
                print(f"Streamed row ({streamed_count + 1}): {row}")
                streamed_count += 1
                if streamed_count >= 15:
                    print("... (stopped after 15 rows from stream)")
                    break
            
            connection_to_prodev.close()
            print("\nDatabase connection closed.")
        else:
            print("Failed to connect to ALX_prodev database.")
    else:
        print("Failed to connect to MySQL server initially.")

    print("\n--- Script finished ---")
    ```

5.  **Run the script:**
    ```bash
    chmod +x database-adv-script/0-main.py
    ./database-adv-script/0-main.py
    ```
    You will see output demonstrating the database setup, data insertion, and then the individual streaming of data rows via the generator.

---

## Task 2: Complex Queries with Joins

**Objective:** Master SQL joins by writing complex queries using different types of joins (INNER, LEFT, FULL OUTER).

### Setup and Running:

1.  **Create `joins_queries.sql`:**
    Create a file named `joins_queries.sql` in the `database-adv-script` directory with the following SQL content:

    ```sql
    -- Use the alx_airbnb_database
    -- This line assumes your database is already created.
    -- If not, you might need to create it first: CREATE DATABASE IF NOT EXISTS alx_airbnb_database;
    USE alx_airbnb_database;

    -- =====================================================================
    -- Query 1: INNER JOIN
    -- Objective: Retrieve all bookings and the respective users who made those bookings.
    -- Description: An INNER JOIN returns only the rows where there is a match in both tables
    --              based on the join condition. In this case, it will show bookings that
    --              are definitely linked to an existing user.
    -- =====================================================================
    SELECT
        b.booking_id,
        b.start_date,
        b.end_date,
        u.user_id,
        u.username,
        u.email
    FROM
        bookings AS b
    INNER JOIN
        users AS u ON b.user_id = u.user_id;

    -- =====================================================================
    -- Query 2: LEFT JOIN
    -- Objective: Retrieve all properties and their reviews, including properties that have no reviews.
    -- Description: A LEFT JOIN (or LEFT OUTER JOIN) returns all rows from the left table
    --              (properties in this case) and the matching rows from the right table (reviews).
    --              If there is no match in the right table, NULLs are returned for the
    --              right table's columns.
    -- =====================================================================
    SELECT
        p.property_id,
        p.name AS property_name,
        p.city,
        r.review_id,
        r.rating,
        r.comment,
        r.user_id AS reviewer_user_id -- User who wrote the review
    FROM
        properties AS p
    LEFT JOIN
        reviews AS r ON p.property_id = r.property_id;

    -- =====================================================================
    -- Query 3: FULL OUTER JOIN (Simulated for MySQL)
    -- Objective: Retrieve all users and all bookings, even if the user has no booking
    --            or a booking is not linked to a user.
    -- Description: MySQL does not natively support FULL OUTER JOIN. It must be simulated
    --              by combining a LEFT JOIN and a RIGHT JOIN using UNION.
    --              - The LEFT JOIN part gets all users and their bookings (including users with no bookings).
    --              - The RIGHT JOIN part gets all bookings and their users, then filters to include
    --                only those bookings that *do not* have a matching user in the LEFT JOIN result
    --                (i.e., bookings with a NULL user_id or a user_id not present in the users table).
    --              - UNION combines these two result sets, removing duplicate rows.
    -- =====================================================================
    SELECT
        u.user_id,
        u.username,
        u.email,
        b.booking_id,
        b.start_date,
        b.end_date,
        b.property_id
    FROM
        users AS u
    LEFT JOIN
        bookings AS b ON u.user_id = b.user_id

    UNION

    SELECT
        u.user_id,
        u.username,
        u.email,
        b.booking_id,
        b.start_date,
        b.end_date,
        b.property_id
    FROM
        users AS u
    RIGHT JOIN
        bookings AS b ON u.user_id = b.user_id
    WHERE
        u.user_id IS NULL;
    ```

2.  **Prepare `alx_airbnb_database`:**
    * Connect to your MySQL client.
    * Create the `alx_airbnb_database`:
        ```sql
        CREATE DATABASE IF NOT EXISTS alx_airbnb_database;
        USE alx_airbnb_database;
        ```
    * **Crucially, create the `users`, `properties`, `bookings`, and `reviews` tables** within this database based on the "Assumed Database Schemas" section above. You'll also need to **insert sample data** into these tables to properly test the joins (e.g., users with no bookings, properties with no reviews, bookings with invalid user IDs if you want to test the full outer join edge cases).

3.  **Run the SQL Queries:**
    You can execute these queries by copying and pasting them directly into your MySQL client, or by sourcing the file:
    ```bash
    mysql -u your_mysql_user -p alx_airbnb_database < database-adv-script/joins_queries.sql
    ```
    (Replace `your_mysql_user` with your actual MySQL username)

## Troubleshooting Common Issues

* **`KeyError: 'localhost'` or similar for `DB_CONFIG`:**
    This happens if you incorrectly reference keys in `DB_CONFIG` (e.g., `DB_CONFIG['localhost']` instead of `DB_CONFIG['host']`). Ensure you are using `DB_CONFIG['host']`, `DB_CONFIG['user']`, and `DB_CONFIG['password']`.
* **`SyntaxError: leading zeros in decimal integer literals...`:**
    This means you've accidentally pasted the `user_data.csv` content directly into your Python script (`seed.py`). The CSV data *must* be in a separate file named `user_data.csv` in the same directory as your script.
* **`Error Code: 1046. No database selected`:**
    When running SQL queries directly in a MySQL client, you need to first tell MySQL which database to operate on using `USE database_name;` (e.g., `USE ALX_prodev;`) before creating tables or inserting data if you're not specifying the database name in the query itself (e.g., `CREATE TABLE ALX_prodev.user_data ...`). Also, ensure your `CREATE TABLE` statement correctly specifies the table name (`user_data`) and not the database name (`ALX_prodev`).

This `README.md` should provide a comprehensive guide for anyone looking to understand and replicate your work.
