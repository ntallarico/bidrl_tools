from config import local_ip_address
import os

def launch_webapp(ip = local_ip_address, port = '8000'):
    print(f"launching webapp on {ip}:{port}")
    os.system(f"python .\\bidrl_tools_webapp\\manage.py runserver {ip}:{port}")

def main():
    launch_webapp()

if __name__ == "__main__":
    main()
