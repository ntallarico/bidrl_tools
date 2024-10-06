import sys
import os
import sqlite3

# tell this file that the root directory is two folder levels up so that it can read our files like config, bidrl_classes, etc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import bidrl_functions as bf


conn = bf.init_sqlite_connection()
cursor = conn.cursor()



# def drop_rows_with_zero_or_null_max_desired_bid(conn):
#     try:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM items_user_input WHERE max_desired_bid = 0 OR max_desired_bid IS NULL")
#         conn.commit()
#         print("Rows with max_desired_bid = 0 or NULL have been successfully deleted.")
#     except Exception as e:
#         print(f"An error occurred while deleting rows: {e}")
#         conn.rollback()
# drop_rows_with_zero_or_null_max_desired_bid(conn)



# def fetch_and_insert_items_into_items_user_input():
#     # Fetch items where highbidder_username = 'ndt'
#     cursor.execute("SELECT * FROM items WHERE highbidder_username = 'ndt'")
#     items = cursor.fetchall()

#     # Insert items into items_user_input table
#     for item in items:
#         cursor.execute('''
#             INSERT OR IGNORE INTO items_user_input (item_id, auction_id, description, url, end_time_unix, item_bid_group_id, ibg_items_to_win, cost_split, max_desired_bid, notes)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (
#             item['item_id'],
#             item['auction_id'],
#             item['description'],
#             item['url'],
#             item['end_time_unix'],
#             '',
#             '',
#             '',
#             '',
#             ''
#         ))

#     # Commit the transaction and close the connection
#     conn.commit()
#     conn.close()

# fetch_and_insert_items_into_items_user_input()


# def create_and_populate_new_database():
#     # Path for the new database
#     new_db_path = 'bidrl_user_input.sqlite'
    
#     # Path for the existing database (assuming it's in the same directory)
#     existing_db_path = 'bidrl.sqlite'
    
#     # Create a new database and connect to it
#     new_conn = bf.init_sqlite_connection(database = 'bidrl_user_input')
#     new_cursor = new_conn.cursor()
    
#     # Connect to the existing database
#     existing_conn = conn
#     existing_cursor = existing_conn.cursor()
    
#     try:
#         # Get the schema of the existing table
#         existing_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='items_user_input'")
#         create_table_sql = existing_cursor.fetchone()[0]
        
#         # Create the new table in the new database
#         new_cursor.execute(create_table_sql)
        
#         # Copy data from the existing table to the new table
#         existing_cursor.execute("SELECT * FROM items_user_input")
#         rows = existing_cursor.fetchall()
        
#         # Get column names
#         column_names = [description[0] for description in existing_cursor.description]
#         placeholders = ', '.join(['?' for _ in column_names])
        
#         # Insert data into the new table
#         insert_sql = f"INSERT INTO items_user_input ({', '.join(column_names)}) VALUES ({placeholders})"
#         new_cursor.executemany(insert_sql, rows)
        
#         # Commit changes and close connections
#         new_conn.commit()
#         print(f"Successfully created and populated {new_db_path} with data from {existing_db_path}")
#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
#     finally:
#         new_conn.close()
#         existing_conn.close()

# # Call the function to create and populate the new database
# create_and_populate_new_database()
