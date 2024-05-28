'''
This script runs all setup steps needed for the other scripts to run properly

'''

import os
import bidrl_functions as bf


# install required python libraries
print("\nInstalling required python libraries.\n")
os.system('pip install -r requirements.txt')


# check if needed directories exist and create them if they do not
bf.ensure_directory_exists('local_files')
bf.ensure_directory_exists('local_files/auto_bid')



