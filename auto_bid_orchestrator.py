import subprocess
import psutil
import time


# Check if there is any running process that matches the given pid
def is_process_running(pid):
    return psutil.pid_exists(pid)

# Ensure auto_bid.py is always running
def run_script():
    # Start auto_bid.py and get the process ID
    process = subprocess.Popen(['python', 'auto_bid.py'])
    pid = process.pid
    print(f"Started auto_bid.py with PID: {pid}")

    while True:
        if not is_process_running(pid):
            print(f"Process with PID {pid} (auto_bid.py) is not running. Starting now...")
            process = subprocess.Popen(['python', 'auto_bid.py'])
            pid = process.pid
            print(f"Restarted auto_bid.py with new PID: {pid}")
        else:
            print(f"Process with PID {pid} (auto_bid.py) is currently running.")

        time.sleep(20) # wait 20 seconds before checking again

if __name__ == "__main__":
    run_script()