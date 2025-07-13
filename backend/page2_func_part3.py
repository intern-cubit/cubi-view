# This script contains features like 
# 1. USB Port enabling and disabling
# 2. Lunch mode on and off

##### USB Port enable and disable ##########
import winreg
import os

def disable_usb_ports():
    """Disable USB storage devices by modifying the Windows Registry."""
    try:
        # Open the USBSTOR registry key with write access
        key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Set the Start value to 4 to disable USB storage
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
        winreg.CloseKey(key)
        
        print("USB storage devices disabled successfully.Restart may be required.")
        return True
    except PermissionError:
        print("Error: Administrative privileges required to modify the registry.")
        return False
    except Exception as e:
        print(f"Error disabling USB ports: {e}")
        return False

def enable_usb_ports():
    """Enable USB storage devices by modifying the Windows Registry."""
    try:
        # Open the USBSTOR registry key with write access
        key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Set the Start value to 3 to enable USB storage
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
        winreg.CloseKey(key)
        
        print("USB storage devices enabled successfully.Restart may be required.")
        return True
    except PermissionError:
        print("Error: Administrative privileges required to modify the registry.")
        return False
    except Exception as e:
        print(f"Error enabling USB ports: {e}")
        return False


############### Lunch hour start and stop #################

import json
import time
import os
import threading
from datetime import datetime, timedelta
import pytz
from pathlib import Path
from credentials import REPORT_DIR, CONFIG_PATH, BACKUP_FILE_PATH
from write_report import write_report

# ========== File Paths and Timezone ==========


IST = pytz.timezone("Asia/Kolkata")

# ========== Global State ==========
lunch_monitor_thread = None
lunch_monitor_running = False

# ========== Config Helpers ==========
def load_config():
    if not os.path.exists(CONFIG_PATH):
        default_config = {"Lunch Break Mode": False}
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

# ========== Lunch Timer Core ==========
def start_lunch_timer():
    def task():
        print("[Lunch Timer] Waiting until 2 PM IST to restore features...")
        while True:
            now_ist = datetime.now(IST)
            if now_ist.hour >= 14:
                break
            time.sleep(30)

        # Calculate delay
        actual_time = datetime.now(IST)
        expected_time = actual_time.replace(hour=14, minute=0, second=0, microsecond=0)
        delay_seconds = max(0, int((actual_time - expected_time).total_seconds()))

        # Restore full config from backup
        if os.path.exists(BACKUP_FILE_PATH):
            try:
                with open(BACKUP_FILE_PATH, "r") as f:
                    backup_config = json.load(f)
                save_config(backup_config)
                print("[Lunch Timer] Full config restored from backup.")

                # Log
                log_lines = [
                    f"Restore Time (IST): {actual_time.strftime('%Y-%m-%d %H:%M:%S')}",
                    f"Delay from 2:00 PM: {str(timedelta(seconds=delay_seconds))}",
                    f"Restored Features ({len(backup_config)}):"
                ] + [f" - {feat}: {str(val)}" for feat, val in backup_config.items()]

                write_report(
                    directory=REPORT_DIR,
                    base_filename="lunch_restore_report",
                    content=log_lines,
                    title="🍴 Lunch Monitoring Resume Log",
                    with_timestamp=True,
                    mode='a'
                )
            except Exception as e:
                print(f"[Lunch Timer] Error restoring config: {e}")

    threading.Thread(target=task, daemon=True).start()

# ========== Enable / Disable Monitor ==========
def enable_lunch_mode_monitor():
    global lunch_monitor_thread, lunch_monitor_running

    if lunch_monitor_running:
        print("[Lunch Monitor] Already running.")
        return

    lunch_monitor_running = True

    def monitor():
        while lunch_monitor_running:
            now = datetime.now(IST)
            if now.hour == 15 and now.minute == 0:
                print("[Lunch Monitor] 1 PM reached. Triggering lunch timer...")

                # Step 1: Backup full config BEFORE modifying it
                config = load_config()
                with open(BACKUP_FILE_PATH, "w") as f:
                    json.dump(config, f, indent=4)
                print("[Lunch Monitor] Full config backed up.")

                # Step 2: Disable all features except 'Lunch Break Mode'
                new_config = {key: False for key in config}
                if config.get("Lunch Break Mode", False):
                    new_config["Lunch Break Mode"] = True
                save_config(new_config)
                print("[Lunch Monitor] Config overwritten with lunch-disabled state.")

                # Step 3: Start lunch timer
                start_lunch_timer()
                return

            time.sleep(30)

    lunch_monitor_thread = threading.Thread(target=monitor, daemon=True)
    lunch_monitor_thread.start()
    print("[Lunch Monitor] Monitor thread started.")

def disable_lunch_mode_monitor():
    global lunch_monitor_running, lunch_monitor_thread
    lunch_monitor_running = False
    if lunch_monitor_thread and lunch_monitor_thread.is_alive():
        lunch_monitor_thread.join(timeout=1)
    print("[Lunch Monitor] Monitor thread stopped.")


