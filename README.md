# bidrl_tools
Set of tools for usage of BidRL. Scraping, processing of invoices, etc

Setup:
1. Create file config.py in repo. Populate it as such:

    user_email = 'your email'
   
    user_password = 'your password'

    google_form_link_base = 'google form link for expense input'

    sql_server_name = 'name of sql server in which database resides'

    sql_database_name = 'name of database in which to create schema for all bidrl data'

    sql_admin_username = 'admin account username'

    sql_admin_password = 'admin account password'

2. Set up a folder local_files in repo.

3. pip install -r requirements.txt