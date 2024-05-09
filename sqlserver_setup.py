'''
This script sets up the sql schema from scratch given a server, database, and user account.
All edits I make to the schema will be made here via code, so that this script could be run and recreate the entire schema from a blank database.

It requires a server name, database name, username, and password for an admin account on the database. This information goes in config.py.

This script will make no changes to a database already in the goal state.
'''

import pyodbc
from config import sql_server_name, sql_database_name, sql_admin_username, sql_admin_password


# returns: 1 if table exists in database.schema and 0 if it does not
def check_if_table_exists(conn, sql_schema_name, table_name):
    cursor = conn.cursor()
    print(f"\nChecking to see if table exists: {sql_schema_name}.{table_name}")
    cursor.execute(f'''
        SELECT IIF(EXISTS (
            SELECT * FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{sql_schema_name}'
            AND TABLE_NAME = '{table_name}'
        ), 1, 0) AS status;
    ''')
    result = cursor.fetchone()
    if result:
        if result[0] == 1: return 1
        else: return 0
    else:
        print("error getting result in check_if_table_exists(). Exiting.")
        quit()


# returns: 1 if schema exists in database and 0 if it does not
def check_if_schema_exists(conn, schema_name):
    cursor = conn.cursor()
    print(f"\nChecking to see if schema exists: {schema_name}")
    cursor.execute(f'''
        SELECT IIF(EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema_name}'), 1, 0) AS status;
    ''')
    result = cursor.fetchone()
    if result:
        if result[0] == 1: return 1
        else: return 0
    else:
        print("error getting result in check_if_schema_exists(). Exiting.")
        quit()


# drops the entire schema including all of its contents
def drop_entire_schema(conn, schema_name):
    cursor = conn.cursor()
    print(f"\nDropping schema {schema_name} and its entire contents.")
    # drop all tables in the schema first
    cursor.execute(f'''
        DECLARE @sql NVARCHAR(MAX) = '';
        SELECT @sql += 'DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + '; '
        FROM sys.tables
        WHERE schema_id = SCHEMA_ID('{schema_name}');
        EXEC sp_executesql @sql;
    ''')
    # drop the schema
    cursor.execute(f'''
        IF EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema_name}')
            EXEC('DROP SCHEMA {schema_name}')
    ''')
    conn.commit() # save changes to database


# creates schema, checking if it already exists first
def create_bidrl_schema(conn, schema_name):
    cursor = conn.cursor()
    # check if the schema exists
    if check_if_schema_exists(conn, schema_name) == 1:
        print(f"Already exists. Skipping creation.")
    else:
        print(f"Does not exist. Creating schema: {schema_name}")
        cursor.execute(f'''
            CREATE SCHEMA {schema_name}
        ''')
    conn.commit() # save changes to database


# creates table for items in schema, checking if it already exists first
def create_items_table(conn, schema_name, items_table_name):
    cursor = conn.cursor()
    if check_if_table_exists(conn, schema_name, items_table_name) == 1:
        print(f"Already exists. Skipping creation.")
    else:
        print(f"Does not exist. Creating table: {schema_name}.{items_table_name}")
        cursor.execute(f'''
            USE {sql_database_name};
            CREATE TABLE {schema_name}.{items_table_name} (
                item_id INT PRIMARY KEY,
                description NVARCHAR(255),
                auction_id INT,
                end_time_unix BIGINT,
                url NVARCHAR(255)
            )
        ''')
    conn.commit() # save changes to database




def sqlserver_setup():
    print(f"\nEstablishing connection to server {sql_server_name}, database {sql_database_name}, user {sql_admin_username}")
    # set up connection string
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                        f'SERVER={sql_server_name};'
                        f'DATABASE={sql_database_name};'
                        f'UID={sql_admin_username};'
                        f'PWD={sql_admin_password}')

    schema_name = 'bidrl'
    items_table_name = 'Items'

    # this is only called here for debugging! remove before production!
    drop_entire_schema(conn, schema_name)


    create_bidrl_schema(conn, schema_name)


    create_items_table(conn, schema_name, items_table_name)


    
    cursor = conn.cursor()
    # continue development of new table creation code here and then move to functions





if __name__ == "__main__":
    sqlserver_setup()









# commits the current transaction to the database
# this means that all the operations performed in the transaction are permanently saved in the database
#conn.commit()