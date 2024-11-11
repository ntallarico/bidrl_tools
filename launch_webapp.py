import os
import bidrl_functions as bf

def launch_webapp(port = '8000'):
    try:
        local_ip_address = bf.get_local_ip()
        print(f"Launching webapp on {local_ip_address}:{port}")
        #os.system(f"python .\\bidrl_tools_webapp\\manage.py runserver {local_ip_address}:{port}")
        os.system(f"cd bidrl_tools_webapp && uvicorn bidrl_tools_webapp.asgi:application --host {local_ip_address} --port {port}")
    except Exception as e:
        print(f"Error launching webapp: {e}")
        input("\nPress Enter to close...")

def main():
    print("Local IP Address:", bf.get_local_ip())
    launch_webapp()

if __name__ == "__main__":
    main()
