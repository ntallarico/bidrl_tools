import sqlite3


# returns: 1 if table exists in database and 0 if it does not
def check_if_table_exists(conn, table_name):
    cursor = conn.cursor()
    print(f"\nChecking if table exists: {table_name}")
    cursor.execute(f'''
        SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='{table_name}';
    ''')
    result = cursor.fetchone()
    if result:
        if result[0] == 1: return 1
        else: return 0
    else:
        print("error getting result in check_if_table_exists(). Exiting.")
        quit()

def drop_database(conn):
    cursor = conn.cursor()
    print("\nDropping all tables in the database.")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"Dropping table: {table[0]}")
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
    print("All tables dropped successfully.")



def sql_database_setup():
    conn = sqlite3.connect('local_files/bidrl.db') # connect to SQLite database (or create if not exists)
    cursor = conn.cursor()

    drop_database(conn) # this is only called here for debugging! remove before production!

    # create affiliates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            affiliate_id TEXT PRIMARY KEY,
            affiliate_name TEXT
        );
    ''')
    conn.commit()

    # create auctions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auctions (
            auction_id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            item_count INTEGER,
            start_datetime TEXT,
            status TEXT
        );
    ''')
    conn.commit()

    # create items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY,
            auction_id TEXT,
            description TEXT,
            current_bid REAL,
            highbidder_username TEXT,
            url TEXT,
            tax_rate REAL,
            buyer_premium REAL,
            lot_number TEXT,
            bidding_status TEXT,
            end_time_unix INTEGER,
            bid_count INTEGER,
            is_favorite INTEGER,
            total_cost REAL,
            cost_split TEXT,
            max_desired_bid REAL
        );
    ''')
    conn.commit()

    # create bids table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bids (
            bid_id TEXT PRIMARY KEY,
            item_id TEXT,
            username TEXT,
            bid REAL,
            bid_time TEXT,
            time_of_bid TEXT,
            time_of_bid_unix INTEGER,
            buyer_number TEXT,
            description TEXT
        );
    ''')
    conn.commit()

    # create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            date TEXT,
            link TEXT,
            total_cost REAL,
            expense_input_form_link TEXT
        );
    ''')
    conn.commit()

    # create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY
            , user_id INTEGER
        );
    ''')
    conn.commit()
    
    conn.close()



if __name__ == "__main__":
    sql_database_setup()



'''
Database plans:
so if I want to do postgres or sqlserver, I will have to have the user install them and sping them up first.
but if I want to do sqlite, I can do that purely in script.

so if I have to get user to install something either way, I'd do sql server over postgresql.
however, lets compare sqlite to sql server and see if I actually need sql server

pros and cons on sqlserver vs sqlite:
- sqlite requires no user configuration or other setup other than running my script
- sqlite is much less resource intensive
- sqlite stores its data in a single file, making it super portable
- sqlite is a file format that is self-contained and can be used without any other software
- sqlite cannot have multiple users access it at once, but that's ok for this
- sqlite I have read works with "moderate" database size. which I think is good for this project

I will use sqlite for now. It will allow me to have the user simply run a script to set it all up
and will store the entire database in a single file, making it more portable.
If I ever have a need for some massive scale increase or multiple users writing/reading to it at once,
then I'll shift to postgres or sql server.

'''

