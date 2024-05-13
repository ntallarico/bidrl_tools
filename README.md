# bidrl_tools
Set of tools for usage of BidRL. Scraping, processing of invoices, etc

Setup:
1. Create file config.py in repo. Populate it as such:

    user_email = 'your email'
   
    user_password = 'your password'

    google_form_link_base = 'google form link for expense input'

2. Set up a folder local_files in repo.

3. pip install -r requirements.txt

4. To scrape all of bidrl's data into a relational database: run database_setup.py, then run gigascrape.py. You can view the sqlite database using a tool like https://sqlitebrowser.org/dl/