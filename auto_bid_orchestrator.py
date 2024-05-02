import subprocess
import psutil
import time

def find_process(name):
    """Check if there is any running process that contains the given name."""
    for proc in psutil.process_iter(['name']):
        if name in proc.info['name']:
            return True
    return False

def run_script():
    """Ensure auto_bid.py is always running."""
    while True:
        if not find_process('auto_bid.py'):
            print("auto_bid.py is not running. Starting now...")
            subprocess.Popen(['python', 'auto_bid.py'])
        else:
            print("auto_bid.py is currently running.")
        
        # Check every 10 seconds
        time.sleep(10)

if __name__ == "__main__":
    run_script()