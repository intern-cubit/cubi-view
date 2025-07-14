import os
import sys
import json
import time
import threading
import socket
import requests
import ctypes
import win32serviceutil
import win32service
import win32event
import servicemanager

from credentials import ACTIVATION_PATH
from main import start_main
from get_systemID import get_system_id

API_URL = "https://api-keygen.obzentechnolabs.com/api/sadmin/check-activation"
SERVICE_NAME = "ActivatorService"

# === Elevation Logic ===
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        return False  # Current process exits; elevated one starts
    except Exception as e:
        print("[!] Failed to elevate to admin:", e)
        return False

# === Activation Check ===  
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def is_activated():
    if not os.path.exists(ACTIVATION_PATH):
        return False
    try:
        with open(ACTIVATION_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("[!] Failed to load activation file:", e)
        return False

    system_id = get_system_id()
    data["systemId"] = system_id

    try:
        with open(ACTIVATION_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        servicemanager.LogErrorMsg(f"Failed to update activation file: {e}")

    payload = {
        "systemId": system_id,
        "appName": "Cubi-View",
    }

    try:
        res = requests.post(API_URL, json=payload, timeout=10)
        res_json = res.json()
        return res_json.get("success") and res_json.get("activationStatus") == "active"
    except Exception as e:
        servicemanager.LogErrorMsg(f"Activation check failed: {e}")
        return False

# === Monitoring Loop ===
def run_start_main_forever():
    t = threading.Thread(target=start_main, daemon=False)
    t.start()
    try:
        while True:
            time.sleep(60)
    except Exception as e:
        servicemanager.LogErrorMsg(f"Main loop error: {e}")

# === Windows Service Class ===
class ActivatorService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = "Activator Protection Service"
    _svc_description_ = "Protects and monitors CubiView software."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("ActivatorService started.")
        while not is_connected():
            servicemanager.LogInfoMsg("Waiting for internet...")
            time.sleep(5)

        if is_activated():
            servicemanager.LogInfoMsg("System activated. Starting monitoring...")
            run_start_main_forever()
        else:
            servicemanager.LogErrorMsg("Activation failed.")

# === Auto-Restart Setup ===
def setup_service_autorestart():
    os.system(f'sc failure "{SERVICE_NAME}" reset= 0 actions= restart/5000')

if __name__ == '__main__':
    if not run_as_admin():
        sys.exit(0)

    # Check if the service is already installed
    try:
        win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        service_exists = True
    except Exception:
        service_exists = False

    if not service_exists:
        print("[+] Installing service...")
        win32serviceutil.InstallService(
            pythonClassString='activator.ActivatorService',
            serviceName=SERVICE_NAME,
            displayName="Activator Protection Service",
            description="Protects and monitors CubiView software.",
            startType=win32service.SERVICE_AUTO_START
        )
        setup_service_autorestart()
        print("[+] Service installed.")

    try:
        print("[+] Starting service...")
        win32serviceutil.StartService(SERVICE_NAME)
        print("[✓] Service started.")
    except Exception as e:
        print(f"[!] Failed to start service: {e}")