import subprocess
import psutil
import time
import ctypes
import os


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

def kill_firefox_instance_by_identifier(webdriver_identifier):
    print(f"Attempting to kill all firefox instances with custom identifier: {webdriver_identifier}")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'firefox.exe' and f'--custom-identifier={webdriver_identifier}' in proc.info['cmdline']:
                print(f"Killing process {proc.info['pid']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def count_firefox_instances_by_identifier(webdriver_identifier):
    count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'firefox.exe' and f'--custom-identifier={webdriver_identifier}' in proc.info['cmdline']:
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return count

def run_auto_bid():
    # must be the same identifier used in auto_bid.py to label create firefox instances
    webdriver_identifier = 'auto_bid'

    print("\nPreventing machine from sleeping.")
    prevent_sleep()

    # start auto_bid.py and get the process ID
    process = subprocess.Popen(['python', 'auto_bid.py'])
    pid = process.pid
    print(f"\nStarted auto_bid.py with PID: {pid}")

    try:
        while True:

            # check if auto_bid.py is still running. if it is not, kill all firefox instances with webdriver_identifier and restart auto_bid.py
            if not is_process_running(pid):
                print(f"\nProcess with PID {pid} (auto_bid.py) is not running")

                # Kill all Firefox instances with the custom identifier
                kill_firefox_instance_by_identifier(webdriver_identifier = webdriver_identifier)

                # Restart auto_bid.py
                print("\nRestarting auto_bid.py")
                process = subprocess.Popen(['python', 'auto_bid.py'])
                pid = process.pid
                print(f"Restarted auto_bid.py with new PID: {pid}")

            # count firefox instances currently open by auto_bid.py. if it is above a threshold, then kill auto_bid.py
            # for reference, get_logged_in_webdriver() should generate 2 "instances"
            auto_bid_firefox_instance_count = count_firefox_instances_by_identifier(webdriver_identifier)
            #print(f"auto_bid firefox instance count: {auto_bid_firefox_instance_count}")
            if auto_bid_firefox_instance_count > 4: # arbitrarily chose 4 instead of the 2 that we expect to see. for wiggle room I guess?
                print(f"Too many auto_bid Firefox instances open ({auto_bid_firefox_instance_count}).")
                print(f"Killing all child processes of auto_bid.py process with PID: {pid}")
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.kill()
                print(f"Killing auto_bid.py process with PID: {pid}")
                process.kill()
                kill_firefox_instance_by_identifier(webdriver_identifier = webdriver_identifier)

            time.sleep(10)  # wait 10 seconds before checking again
    finally:
        print("\nReturning Windows power settings to user's default.")
        allow_sleep()

if __name__ == "__main__":
    run_auto_bid()