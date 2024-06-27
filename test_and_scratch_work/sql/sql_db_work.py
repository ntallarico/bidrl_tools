import sys
import os
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
