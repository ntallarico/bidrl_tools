'''
This script is used to gather input about items from the user.
It creates/re-writes/reads a csv file containing all items in the database, allowing the user to input information in columns in that file.
It is then used to read that file and update the user input columns in the items table in the database.
'''

import os
import csv
import sqlite3
import bidrl_functions as bf
from bidrl_classes import Item

# define the list of user input columns. these need to be implemented in the 'Items' class and also exist in the 'items' table in the db
# we list these columns here to specify which values from the csv to actually update in the db
user_input_columns = ['cost_split', 'max_desired_bid', 'notes']


def validate_user_input_columns_in_class(user_input_columns):
    # Check if these fields are properties in the Items class
    missing_properties = [col for col in user_input_columns if not hasattr(Item(), col)]
    if missing_properties:
        print(f"Error: The following properties are missing in the Items class: {', '.join(missing_properties)}. Please implement them in 'Item' in bidrl_classes.py and try again.")
        exit(1)

# Check if these fields exist in the items table in the database
def validate_user_input_columns_in_db(conn, user_input_columns):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(items)")
    columns_info = cursor.fetchall()
    existing_columns = [info[1] for info in columns_info]

    for column in user_input_columns:
        if column not in existing_columns:
            choice = input(f"Column '{column}' does not exist in the items table. Do you want to add it? (yes/no): ")
            if choice.lower() == 'yes':
                cursor.execute(f"ALTER TABLE items ADD COLUMN {column} TEXT")
                conn.commit()
                print(f"Column '{column}' has been added to the items table.")
            else:
                print(f"Error: Column '{column}' does not exist in the items table. Please fix the column name list.")
                exit(1)

def check_file_exists(file_path):
    return os.path.exists(file_path)

def get_user_choice(file_path):
    while True:
        choice = input(f"The file '{file_path}' already exists. Do you want to: (1) replace it with a blank updated copy, or (2) load values from it into the database? Enter 1 or 2: ")
        if choice in ['1', '2']:
            return choice
        else:
            print("Invalid input. Please enter 1 or 2.")

def rewrite_csv_with_db_data(conn, file_path):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    cursor.execute("PRAGMA table_info(items)")
    columns_info = cursor.fetchall()
    existing_columns = [info[1] for info in columns_info]

    # Filter user_input_columns to only include columns that do not already exist in the items table
    filtered_user_input_columns = [col for col in user_input_columns if col not in existing_columns]

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header including user input columns
        writer.writerow(existing_columns + filtered_user_input_columns)
        for item in items:
            # Add empty columns for user input columns
            writer.writerow(list(item) + ['' for _ in filtered_user_input_columns])

def update_db_from_csv(conn, file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor = conn.cursor()
            # Prepare the update statement dynamically based on user input columns
            update_statement = f"""
                UPDATE items
                SET {', '.join([f"{col} = ?" for col in user_input_columns])}
                WHERE item_id = ?
            """
            cursor.execute(update_statement, [row[col] for col in user_input_columns] + [row['item_id']])
        conn.commit()

def gather_user_input_main():
    file_path = 'local_files/items_list_for_user_input.csv'
    conn = bf.init_sqlite_connection()

    validate_user_input_columns_in_class(user_input_columns)
    validate_user_input_columns_in_db(conn, user_input_columns)

    if check_file_exists(file_path):
        choice = get_user_choice(file_path)
        if choice == '1':
            rewrite_csv_with_db_data(conn, file_path)
        elif choice == '2':
            update_db_from_csv(conn, file_path)
    else:
        rewrite_csv_with_db_data(conn, file_path)

    conn.close()

if __name__ == "__main__":
    gather_user_input_main()