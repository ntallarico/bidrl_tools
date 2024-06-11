import sqlite3
import bidrl_functions as bf


# drop entire database and all of its contents
def drop_database(conn):
    cursor = conn.cursor()
    print("\nAttempting to drop all tables in the database.")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"Dropping table: {table[0]}")
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
    print("All tables dropped successfully.")


# create user reporting view. drop it if it already exists first
def create_v_reporting_user(conn):
    bf.drop_and_create_view(conn, 'v_reporting_user', '''
        CREATE VIEW v_reporting_user AS

        WITH usernames as (
            SELECT DISTINCT
                username
            FROM bids
        )
        SELECT
            u.username
            , af.company_name
            , ROUND(SUM(i.current_bid), 2) AS total_bid
	        , ROUND(SUM(i.total_cost), 2) AS total_spent
            , COUNT(DISTINCT i.item_id) AS items_bought
            --, COUNT(DISTINCT b.bid_id) AS bids_placed
            --, MIN(b.time_of_bid_unix) AS earliest_bid_time
            --, MAX(b.time_of_bid_unix) AS latest_bid_time
            --, '' AS most_bought_category
            --, '' AS most_spent_category
            --, '' AS closest_snipe
            --, '' AS longest_out_bid_that_won
            , MAX(i.current_bid) AS most_expensive_purchase
            , COUNT(DISTINCT IIF(i.total_cost BETWEEN 0 AND 1.99, i.item_id, NULL)) AS purchase_count_total_cost_0_to_1_99 -- count of purchases with actual cost of $0-1.99
            , COUNT(DISTINCT IIF(i.total_cost BETWEEN 2 AND 4.99, i.item_id, NULL)) AS purchase_count_total_cost_2_to_4_99 -- count of purchases with actual cost of $2-4.99
            , COUNT(DISTINCT IIF(i.current_bid BETWEEN 0 AND 1.99, i.item_id, NULL)) AS purchase_count_bid_0_to_1_99 -- count of purchases with bid amount of $0-1.99
            , COUNT(DISTINCT IIF(i.current_bid BETWEEN 2 AND 4.99, i.item_id, NULL)) AS purchase_count_bid_2_to_4_99 -- count of purchases with bid amount of $2-4.99
            --, COUNT(DISTINCT b.item_id) AS items_bid_on
        FROM usernames u
            LEFT JOIN items i on i.highbidder_username = u.username -- specifically join on items where the user won
            LEFT JOIN auctions au on au.auction_id = i.auction_id
            LEFT JOIN affiliates af on af.affiliate_id = au.affiliate_id
            --LEFT JOIN bids b on b.username = u.username -- join in all bids, regardless of item win status
        WHERE au.status = 'closed'
        GROUP BY
            u.username
            , af.company_name
        ;
    ''')


def sql_database_setup():
    conn = bf.init_sqlite_connection()
    cursor = conn.cursor()


    ##### tables #####

    # create affiliates table
    bf.create_table(conn, 'affiliates', '''
        CREATE TABLE IF NOT EXISTS affiliates (
            affiliate_id TEXT PRIMARY KEY
            , logo TEXT
            , do_not_display_tab INTEGER
            , company_name TEXT
            , firstname TEXT
            , lastname TEXT
            , auc_count INTEGER
        );
    ''')
    

    # create auctions table
    bf.create_table(conn, 'auctions', '''
        CREATE TABLE IF NOT EXISTS auctions (
            auction_id TEXT PRIMARY KEY
            , url TEXT
            , title TEXT
            , item_count INTEGER
            , start_datetime TEXT
            , status TEXT
            , affiliate_id TEXT
            , aff_company_name TEXT
            , state_abbreviation TEXT
            , city TEXT
            , zip TEXT
            , address TEXT
        );
    ''')

    # create items table
    bf.create_table(conn, 'items', '''
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY
            , auction_id TEXT
            , description TEXT
            , current_bid REAL
            , highbidder_username TEXT
            , url TEXT
            , tax_rate REAL
            , buyer_premium REAL
            , lot_number TEXT
            , bidding_status TEXT
            , end_time_unix INTEGER
            , bid_count INTEGER
            , viewed INTEGER
            , is_favorite INTEGER
            , total_cost REAL
            , cost_split TEXT
            , max_desired_bid REAL
            , item_bid_group_id TEXT
        );
    ''')

    # create bids table
    bf.create_table(conn, 'bids', '''
        CREATE TABLE IF NOT EXISTS bids (
            bid_id TEXT PRIMARY KEY
            , item_id TEXT
            , username TEXT
            , bid REAL
            , bid_time TEXT
            , time_of_bid TEXT
            , time_of_bid_unix INTEGER
            , buyer_number TEXT
            , description TEXT
        );
    ''')

    # create invoices table
    bf.create_table(conn, 'invoices', '''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY
            , date TEXT
            , link TEXT
            , total_cost REAL
            , expense_input_form_link TEXT
    );
    ''')

    # create users table
    bf.create_table(conn, 'users', '''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY
            , user_id INTEGER
        );
    ''')

    #create images table
    bf.create_table(conn, 'images', '''
        CREATE TABLE IF NOT EXISTS images (
            item_id TEXT
            , image_url TEXT
            , image_height INTEGER
            , image_width INTEGER
            , PRIMARY KEY (item_id, image_url)
        );
    ''')


    ##### views #####

    print('')

    # create view v_reporting_user
    create_v_reporting_user(conn)


    ##### indexes #####

    print('')

    # create indexes on columns that we commonly use for joining/filtering/sorting. this DRASTICALLY speeds up queries
    # add more indexes here as needed!
    
    bf.create_index(conn, 'affiliates', 'affiliate_id')

    bf.create_index(conn, 'auctions', 'auction_id')
    bf.create_index(conn, 'auctions', 'status')
    bf.create_index(conn, 'auctions', 'affiliate_id')

    bf.create_index(conn, 'items', 'item_id')
    bf.create_index(conn, 'items', 'auction_id')
    bf.create_index(conn, 'items', 'highbidder_username')
    bf.create_index(conn, 'items', 'lot_number')
    bf.create_index(conn, 'items', 'bidding_status')
    bf.create_index(conn, 'items', 'end_time_unix')
    bf.create_index(conn, 'items', 'is_favorite')

    bf.create_index(conn, 'bids', 'bid_id')
    bf.create_index(conn, 'bids', 'item_id')
    bf.create_index(conn, 'bids', 'username')
    bf.create_index(conn, 'bids', 'time_of_bid_unix')

    bf.create_index(conn, 'images', 'item_id')
    
    bf.create_index(conn, 'invoices', 'invoice_id')


    conn.commit()
    conn.close()


def database_setup_main():
    try:
        sql_database_setup()
        print("\nDatabase setup complete.")
    except Exception as e:
        print(f"\nDatabase setup failed with exception: {e}.")
        return 1


if __name__ == "__main__":
    database_setup_main()






'''
Database plans:
my options for databased implementation are sql server, postgres, or sqlite.
postgres or sql server would be more robust, but sqlite would be more lightweight.

if I want to do postgres or sql server, I will have to have the user install them and sping them up first.
but if I want to do sqlite, I can do that purely in script.
I am more familiar with sql server, so if am getting a user to install stuff, then I'd do sqlsever.
lets now compare sql server to sqlite

pros and cons on sql server vs sqlite:
- sqlite requires no user configuration or other setup other than running my script
- sqlite is much less resource intensive
- sqlite stores its data in a single file, making it super portable
- sqlite is a file format that is self-contained and can be used without any other software
- sqlite cannot have multiple users access it at once, but that's ok for this
- sqlite I have read works with "moderate" database size. which I think is good for this project

Conclusion:
I will use sqlite for now. It will allow me to have the user simply run a script to set it all up
and will store the entire database in a single file, making it more portable.
If I ever have a need for some massive scale increase or multiple users writing/reading to it at once,
then I'll shift to sql server (or may postgres).

'''

