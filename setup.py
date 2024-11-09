'''
This script runs all setup steps needed for the other scripts to run properly

'''

import os
import sys
import subprocess

def create_and_activate_venv():
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("\nCreating virtual environment.\n")
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])

    # Activation command (note: this won't persist in the current shell session)
    if os.name == 'nt':  # Windows
        activate_script = '.\\venv\\Scripts\\activate'
    else:  # macOS/Linux
        activate_script = 'source venv/bin/activate'

    print("\nActivating virtual environment.\n")
    os.system(activate_script)

def install_requirements():
    # Install required python libraries
    print("\nInstalling required python libraries.\n")
    pip_executable = os.path.join('venv', 'Scripts', 'pip') if os.name == 'nt' else os.path.join('venv', 'bin', 'pip')
    subprocess.check_call([pip_executable, 'install', '-r', 'requirements.txt'])


def main():
    # create virtual environment and install dependencies first
    create_and_activate_venv()
    install_requirements()

    # import bidrl_functions after requirements have been installed so that referenced libraries work
    import bidrl_functions as bf

    # Check if needed directories exist and create them if they do not
    bf.ensure_directory_exists('local_files')
    bf.ensure_directory_exists('local_files/auto_bid')

    # Set up database by running database_setup.py
    print("\nRunning database setup script.\n")
    python_executable = os.path.join('venv', 'Scripts', 'python') if os.name == 'nt' else os.path.join('venv', 'bin', 'python')
    subprocess.check_call([python_executable, 'database_setup.py'])

    print("\nSetup complete.\n")

if __name__ == '__main__':
    main()