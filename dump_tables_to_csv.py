import sqlite3
import csv
import bidrl_functions as bf


def dump_tables_to_csv(folder_path_for_csvs):
    # connect to SQLite database
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()

    # get list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\nFound {len(tables)} tables:")
    for table in tables:
        print(table[0])

    # loop through the tables and dump each to a CSV file
    for table in tables:
        table_name = table[0] # extract table name from the tuple
        print(f"Working on table: {table_name}")

        # Fetch all data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

        # get column headers
        column_headers = [description[0] for description in cursor.description]

        # define file path for csv
        csv_file_path = f"{folder_path_for_csvs}{table_name}.csv"

        # write data to CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_headers)
            csv_writer.writerows(data)

        print(f"Table {table_name} dumped to {csv_file_path}")

    # close database connection
    print("Completed database dump to CSVs. Closing sqlite connection.")
    conn.close()


def dump_tables_to_csv_main():

    folder_path_data_analysis = 'local_files/data_analysis/'
    bf.ensure_directory_exists(folder_path_data_analysis)

    dump_tables_to_csv(folder_path_data_analysis)
    

if __name__ == "__main__":
    dump_tables_to_csv_main()