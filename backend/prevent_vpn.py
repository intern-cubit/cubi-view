import psutil
import time
from datetime import datetime, timedelta
import subprocess

#from GUI_V2 import authenticate_admin

import threading

vpn_monitoring_enabled = False
vpn_monitoring_thread = None



# List of known VPN process names
vpn_process_names = [
    "openvpn.exe", "wireguard.exe", "vpnui.exe", "vpnagent.exe", "NordVPN.exe", 
    "expressvpn.exe", "vpnclient.exe", "vpnserver.exe", "protonvpn.exe", "SoftEtherVPN.exe",
    "CyberGhost.exe", "ghostvpn.exe",  # CyberGhost VPN
    "pia.exe", "pia_manager.exe",      # Private Internet Access (PIA)
    "Tunnelblick.exe",                 # Tunnelblick (macOS, Windows equivalent may exist)
    "ipvanish.exe", "ipvanishapp.exe",  # IPVanish
    "Surfshark.exe",                   # Surfshark VPN
    "windscribe.exe",                  # Windscribe VPN
    "mullvad.exe",                     # Mullvad VPN
    "vyprvpn.exe",                     # VyprVPN
    "hmas.exe", "hmavpn.exe",           # HideMyAss VPN
    "betternet.exe",                   # Betternet
    "zenmate.exe",                     # ZenMate VPN
    "TunnelBear.exe",                  # TunnelBear VPN
    "pandavpn.exe",                    # Panda VPN
    "perfectprivacy.exe"               # Perfect Privacy VPN
]


# Function to check if any VPN process is running
def is_vpn_running():
    print("Checking for any VPN processes")
    vpn_names_lower = set(name.lower() for name in vpn_process_names)
    for proc in psutil.process_iter(['pid', 'name']):
        pname = proc.info['name'].lower()
        if any(vpn_name in pname for vpn_name in vpn_names_lower):
            return True
        else:
            return False

# Function to handle VPN detection and ask for admin approval
def handle_vpn_detection():
    print("Authentication successful. VPN access granted.")
    unblock_vpn_ports()
    
    # Run timer in a thread
    threading.Thread(target=vpn_timer_task, daemon=True).start()

def vpn_timer_task():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)

    while datetime.now() < end_time:
        if is_vpn_running():
            print(f"VPN is running. Time left: {end_time - datetime.now()}")
            time.sleep(10)
        else:
            print("VPN was closed by the user.")
            return

    print("Time limit reached. Blocking VPN access now.")
    block_vpn()

# Function to block the VPN (Kill VPN processes and disable network interfaces)
def block_vpn():
    print("Blocking VPN...")  
    # Kill all VPN-related processes
    kill_vpn_process()

    # Disable all network adapters related to VPNs
    vpn_adapter_names = get_vpn_adapter_names()
    for adapter in vpn_adapter_names:
        disable_vpn_adapter(adapter)

    # Add firewall rules to block common VPN ports (UDP) - Extra protection
    vpn_ports = [1194, 51820, 443, 1701, 500, 4500]  # Common ports: OpenVPN, WireGuard, L2TP, IPsec
    for port in vpn_ports:
        command = f'netsh advfirewall firewall add rule name="Block VPN Port {port}" dir=out protocol=UDP localport={port} action=block'
        subprocess.run(command, shell=True)
        print(f"Firewall rule added to block UDP port {port}")
    

# Function to kill VPN process immediately
def kill_vpn_process():
    print("Killing VPN process immediately...")
    vpn_names_lower = set(name.lower() for name in vpn_process_names)
    for proc in psutil.process_iter(['pid', 'name']):
        pname = proc.info['name'].lower()
        if any(vpn_name in pname for vpn_name in vpn_names_lower):
            proc.kill()
            print(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")

# Function to get VPN adapter names (heuristically or manually)
def get_vpn_adapter_names():
    vpn_adapters = []
    # Use `netsh` to list all network interfaces and check if they're VPN-related
    result = subprocess.run("netsh interface show interface", shell=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    for line in lines:
        if "VPN" in line or "Virtual" in line:
            # Heuristic to identify VPN adapters; you may need to adapt it to your environment
            parts = line.strip().split()
            adapter_name = " ".join(parts[3:])  # Usually after State, Type, and Interface Name
            vpn_adapters.append(adapter_name)
    print(f"Detected VPN adapters: {vpn_adapters}")
    return vpn_adapters

# Function to disable a specific network adapter
def disable_vpn_adapter(adapter_name):
    print(f"Disabling VPN network adapter: {adapter_name}")
    # Use 'netsh' command to disable the network adapter
    command = f'netsh interface set interface "{adapter_name}" admin=disable'
    subprocess.run(command, shell=True, check=True)
    print(f"Network adapter {adapter_name} disabled.")

# Function to monitor VPN usage and detect VPN access
def monitor_vpn_usage():
    if is_vpn_running():
        block_vpn()
        launch_admin_login(window_title="VPN Access Request",heading="Requesting Admin Approval for VPN Access",
                           on_success=handle_vpn_detection)
    else:
        print("No VPN detected.")

# Function to run VPN monitoring in the background
def start_vpn_monitoring():
    while vpn_monitoring_enabled:   
        monitor_vpn_usage()
        time.sleep(10)


#If the firewall rule has to be deleted after admin approval use the below function
def unblock_vpn_ports():
    vpn_ports = [1194, 51820, 443, 1701, 500, 4500]
    for port in vpn_ports:
        command = f'netsh advfirewall firewall delete rule name="Block VPN Port {port}"'
        subprocess.run(command, shell=True)
        print(f"Firewall rule removed for port {port}")

def enable_vpn_monitoring():
    global vpn_monitoring_enabled, vpn_monitoring_thread
    if vpn_monitoring_enabled:
        print("VPN monitoring is already enabled.")
        return
    vpn_monitoring_enabled = True
    vpn_monitoring_thread = threading.Thread(target=start_vpn_monitoring, daemon=True)
    vpn_monitoring_thread.start()
    print("VPN monitoring ENABLED.")

def disable_vpn_monitoring():
    global vpn_monitoring_enabled
    vpn_monitoring_enabled = False
    unblock_vpn_ports()
    print("VPN monitoring DISABLED.")



from credentials import ACTIVATION_PATH, LOGO_IMAGE

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
import requests


def launch_admin_login(parent_window=None, window_title="Admin Login", 
                       heading="Admin Access Required", sidebar=None, 
                       container=None, on_success=None):
    auth_result = [False]  # mutable flag to track success
    def authenticate():
        entered_username = username_var.get()
        entered_password = password_var.get()

        try:
            res = requests.post(
                "https://api-keygen.obzentechnolabs.com/api/auth/login",
                json={"identifier": entered_username, "password": entered_password},
                timeout=10
            )
            res_data = res.json()
            print("Server response:", res_data)  # debug

            if res.status_code == 200 and "token" in res_data and "user" in res_data:
                auth_result[0] = True  # keep same flag for success

                login_frame.place_forget()
                if sidebar:
                    sidebar.pack(side=tk.LEFT, fill=tk.Y)
                if container:
                    container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                if on_success:
                    on_success()

            else:
                messagebox.showerror("Authentication Failed", res_data.get("message", "Invalid credentials."))

        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")


    # Use existing window or create new one
    root = parent_window if parent_window else tb.Window(themename="cosmo")
    root.title(window_title)
    root.geometry("1000x600")
    root.minsize(800, 500)
    root.iconphoto(False, tk.PhotoImage(file=LOGO_IMAGE))

    # Login Frame centered using `place` for better responsiveness
    login_frame = tb.Frame(root, padding=40)
    login_frame.place(relx=0.5, rely=0.5, anchor="center")
    login_frame.pack_propagate(False)

    # Adjust size proportionally to window
    def resize_frame(event=None):
        width = root.winfo_width()
        height = root.winfo_height()
        login_frame.config(width=int(width * 0.6), height=int(height * 0.75))

    root.bind("<Configure>", resize_frame)
    resize_frame()

    # Grid configuration
    for i in range(3):
        login_frame.grid_columnconfigure(i, weight=1)

    # Logo
    try:
        logo_img = tk.PhotoImage(file=LOGO_IMAGE).subsample(3, 3)
        logo_label = tk.Label(login_frame, image=logo_img)
        logo_label.image = logo_img
        logo_label.grid(row=0, column=0, columnspan=3, pady=(10, 30))
    except Exception as e:
        print("Logo load failed:", e)

    # Heading
    tb.Label(login_frame, text=heading, font=("Poppins", 18, "bold")).grid(row=1, column=0, columnspan=3, pady=(0, 20))

    # Input variables
    username_var = tk.StringVar()
    password_var = tk.StringVar()

    # Grid weights to balance layout
    for i in range(3):
        login_frame.grid_columnconfigure(i, weight=1)

    # Username Label
    tb.Label(login_frame, text="Username", font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", padx=50, pady=5)

    # Username Entry
    tb.Entry(login_frame, textvariable=username_var, width=30).grid(row=2, column=1, padx=(150,5), pady=5)

    # Password Label
    tb.Label(login_frame, text="Password", font=("Segoe UI", 10)).grid(row=3, column=1, sticky="w", padx=50, pady=5)

    # Password Entry
    tb.Entry(login_frame, textvariable=password_var, show="*", width=30).grid(row=3, column=1, padx=(150,5),  pady=5)

    # Authenticate Button
    tb.Button(login_frame, text="Authenticate", bootstyle="success", width=25, command=authenticate).grid(row=4, column=1, pady=20)

    root.mainloop()
    print(auth_result[0])
    return auth_result[0]  # return True if authentication succeeded
    