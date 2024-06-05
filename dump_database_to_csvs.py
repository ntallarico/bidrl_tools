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

    # get list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\nFound {len(tables)} tables in database:")
    for table in tables:
        print(table[0])

    # loop through the tables and dump each to a CSV file
    for table in tables:
        table_name = table[0] # extract table name from the tuple
        print(f"\nWorking on table: {table_name}")

        # Fetch all data from the table
        start_time_select_from_db = time.time()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        print(f"Table {table_name} pulled from database. Time taken: {time.time() - start_time_select_from_db:.4f} seconds")

        # get column headers
        column_headers = [description[0] for description in cursor.description]

        # define file path for csv
        csv_file_path = f"{folder_path_for_csvs}{table_name}.csv"

        # write data to CSV
        start_time_write_csv = time.time()
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_headers)
            csv_writer.writerows(data)

        print(f"Table {table_name} dumped to {csv_file_path}. Time taken: {time.time() - start_time_write_csv:.4f} seconds")

    # close database connection
    print(f"\nCompleted database dump to CSVs. Total time taken: {time.time() - start_time_dump_tables_to_csv:.4f} seconds")
    print("Closing sqlite connection")
    conn.close()


if __name__ == "__main__":
    dump_tables_to_csv('local_files/data_analysis/')