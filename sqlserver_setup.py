import pyodbc



# Set Up Connection


# Connection parameters
server = 'your_server_name'
database = 'BFDB'
username = 'your_username'
password = 'your_password'

# Connection string
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      f'SERVER={server};'
                      f'DATABASE={database};'
                      f'UID={username};'
                      f'PWD={password}')
cursor = conn.cursor()





# Create Tables

cursor.execute('''
CREATE TABLE items (
    item_id INT PRIMARY KEY,
    description NVARCHAR(255),
    auction_id INT,
    end_time_unix BIGINT,
    url NVARCHAR(255)
)
''')
conn.commit()