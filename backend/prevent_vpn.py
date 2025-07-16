import psutil
import time
from datetime import datetime, timedelta
import subprocess
import threading

vpn_monitoring_enabled = False
vpn_monitoring_thread = None
pending_vpn_requests = []  # Store pending admin approval requests



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

# Function to request admin approval for VPN access (API-based)
def request_vpn_admin_approval():
    """
    Add a VPN access request to the pending queue.
    This will be handled by the frontend through API calls.
    """
    request_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "vpn_access_request",
        "message": "VPN detected. Admin approval required for VPN access.",
        "status": "pending"
    }
    pending_vpn_requests.append(request_data)
    print("VPN admin approval request added to queue.")
    return request_data

def approve_vpn_access(request_id=None):
    """
    Approve VPN access and unblock VPN ports.
    Can be called through API with admin authentication.
    """
    try:
        handle_vpn_detection()
        # Remove the request from pending queue if request_id provided
        if request_id:
            global pending_vpn_requests
            pending_vpn_requests = [req for req in pending_vpn_requests if req.get("id") != request_id]
        return True
    except Exception as e:
        print(f"Error approving VPN access: {e}")
        return False

def deny_vpn_access(request_id=None):
    """
    Deny VPN access request.
    """
    try:
        # Remove the request from pending queue if request_id provided
        if request_id:
            global pending_vpn_requests
            pending_vpn_requests = [req for req in pending_vpn_requests if req.get("id") != request_id]
        print("VPN access denied.")
        return True
    except Exception as e:
        print(f"Error denying VPN access: {e}")
        return False

def get_pending_vpn_requests():
    """
    Get all pending VPN access requests.
    """
    return pending_vpn_requests
    
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
        # Instead of launching GUI, add to pending requests queue
        request_vpn_admin_approval()
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

def enable_vpn_monitoring(confirmed: bool = False):
    """
    Enable VPN monitoring with optional confirmation.
    Confirmation must be handled by the frontend and passed as 'confirmed'.
    """
    global vpn_monitoring_enabled, vpn_monitoring_thread
    if vpn_monitoring_enabled:
        print("VPN monitoring is already enabled.")
        return True
        
    if not confirmed:
        print("[VPN Monitoring] Action not confirmed by user. No changes made.")
        return False
    
    vpn_monitoring_enabled = True
    vpn_monitoring_thread = threading.Thread(target=start_vpn_monitoring, daemon=True)
    vpn_monitoring_thread.start()
    print("VPN monitoring started.")
    return True

def disable_vpn_monitoring(confirmed: bool = False):
    """
    Disable VPN monitoring with optional confirmation.
    Confirmation must be handled by the frontend and passed as 'confirmed'.
    """
    global vpn_monitoring_enabled
    if not vpn_monitoring_enabled:
        print("VPN monitoring is already disabled.")
        return True
        
    if not confirmed:
        print("[VPN Monitoring] Action not confirmed by user. No changes made.")
        return False
    
    vpn_monitoring_enabled = False
    print("VPN monitoring stopped.")
    return True

def disable_vpn_monitoring_legacy():
    """Legacy function - use disable_vpn_monitoring(confirmed=True) instead"""
    global vpn_monitoring_enabled
    vpn_monitoring_enabled = False
    unblock_vpn_ports()
    print("VPN monitoring DISABLED.")

# Legacy function signatures for backward compatibility 
# These will be replaced by API-based admin authentication
def launch_admin_login(*args, **kwargs):
    """
    Deprecated: This function has been replaced by API-based admin authentication.
    Use the /api/vpn/admin-request endpoint instead.
    """
    print("WARNING: launch_admin_login is deprecated. Use API-based authentication instead.")
    return False