import os, time
import sqlite3
import csv
import bidrl_functions as bf


def dump_tables_to_csv(folder_path_for_csvs):
    start_time_dump_tables_to_csv = time.time()

    bf.ensure_directory_exists(folder_path_for_csvs)

    # connect to SQLite database
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()

    # get list of all tables and views in the database
    cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');")
    #cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') and name IN ('v_reporting_user');")
    tables_and_views = cursor.fetchall()

    print(f"\nFound {len(tables_and_views)} tables and views in database:")
    for item in tables_and_views:
        print(f"{item[0]} ({item[1]})")

    # loop through the tables and views and dump each to a CSV file
    for item in tables_and_views:
        item_name = item[0]  # extract item name from the tuple
        item_type = item[1]  # extract item type (table or view)
        print(f"\nWorking on {item_type}: {item_name}")

        # Fetch all data from the table or view
        start_time_select_from_db = time.time()
        cursor.execute(f"SELECT * FROM {item_name}")
        data = cursor.fetchall()
        print(f"{item_type.capitalize()} {item_name} pulled from database. Rows: {len(data)}. Time taken: {time.time() - start_time_select_from_db:.4f} seconds.")

        # get column headers
        column_headers = [description[0] for description in cursor.description]

        # define file path for csv
        csv_file_path = f"{folder_path_for_csvs}{item_name}.csv"

        # write data to CSV
        start_time_write_csv = time.time()
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_headers)
            csv_writer.writerows(data)

        print(f"{item_type.capitalize()} {item_name} dumped to {csv_file_path}. Time taken: {time.time() - start_time_write_csv:.4f} seconds.")
    
    # close database connection
    print("\nCompleted database dump to CSVs. Closing sqlite connection.")
    conn.close()

    print(f"\nTotal time taken: {time.time() - start_time_dump_tables_to_csv:.4f} seconds.")


if __name__ == "__main__":
    dump_tables_to_csv('local_files/data_analysis/')