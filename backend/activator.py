# -*- coding: utf-8 -*-
import os
import json
import requests
import sys
import ctypes
import time
import threading
import socket
from datetime import datetime

from credentials import ACTIVATION_PATH, REPORT_DIR
from main import start_main
from get_systemID import get_system_id
from write_report import write_report

API_URL = "https://api-keygen.obzentechnolabs.com/api/sadmin/check-activation"
HEALTH_LOG_FILE = os.path.join(REPORT_DIR, "health.log")

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
        print("[!] Failed to update activation file:", e)

    payload = {
        "systemId": system_id,
        "appName": "Cubi-View",
    }

    try:
        res = requests.post(API_URL, json=payload, timeout=10)
        print("Server response:", res)
        res_json = res.json()
        print("Server response:", res_json)
        return res_json.get("success") and res_json.get("activationStatus") == "active"
    except Exception as e:
        print("[!] Activation check failed:", e)
        return False

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


def run_start_main_forever():
    print("[+] Starting monitoring in background...")

    # Start monitoring in thread
    t = threading.Thread(target=start_main, daemon=False)
    t.start()

    print("[+] Monitoring running. Writing health log every minute.")
    try:
        while True:
            # write_health_log("Monitoring alive for debugging")
            write_report(REPORT_DIR, "health_log", f"Monitoring alive at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", title="Health Log", with_timestamp=True)
            time.sleep(60)
    except Exception as e:
        print("[!] Unexpected exception in health loop:", e)
        # write_health_log(f"Unexpected exception: {e}")
        write_report(REPORT_DIR, "health_log", f"Unexpected exception: {e} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", title="Health Log", with_timestamp=True)


def is_connected():
    try:
        # Try to resolve a DNS (like Google)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

if __name__ == "__main__":
    if not run_as_admin():
        sys.exit()
    # run_start_main_forever()
    # print("[DEBUG] Activation success, starting monitoring...")
            # Wait for internet connection
    print("Checking for internet connection...")
    while not is_connected():
        print("No internet connection. Retrying in 5 seconds...")
        time.sleep(5)
    print("Internet connected!")
    if is_activated():
        print("[DEBUG] Activation success, starting monitoring...")
        run_start_main_forever()
    else:
        print("[!] Activation failed. main.py will not be launched.")