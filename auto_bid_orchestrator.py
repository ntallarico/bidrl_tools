import subprocess
import psutil
import time
import ctypes


# prevents machine from sleeping
def prevent_sleep():
    # ES_CONTINUOUS prevents the system from entering sleep.
    # ES_SYSTEM_REQUIRED forces the system to be awake.
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    )

# returns windows power settings to user's default
def allow_sleep():
    ES_CONTINUOUS = 0x80000000
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS
    )

# check if there is any running process that matches a given pid
def is_process_running(pid):
    return psutil.pid_exists(pid)

# ensure auto_bid.py is always running
def run_auto_bid():
    print("\nPreventing machine from sleeping.")
    prevent_sleep()

    # start auto_bid.py and get the process ID
    process = subprocess.Popen(['python', 'auto_bid.py'])
    pid = process.pid
    print(f"\nStarted auto_bid.py with PID: {pid}")

    try:
        while True:
            if not is_process_running(pid):
                print(f"Process with PID {pid} (auto_bid.py) is not running. Starting now...")
                process = subprocess.Popen(['python', 'auto_bid.py'])
                pid = process.pid
                print(f"Restarted auto_bid.py with new PID: {pid}")
            #else: print(f"Process with PID {pid} (auto_bid.py) is currently running.")

            time.sleep(10) # wait 20 seconds before checking again
    finally:
        print("\nReturning Windows power settings to user's default.")
        allow_sleep()

if __name__ == "__main__":
    run_auto_bid()