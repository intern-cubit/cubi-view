import psutil
import time
import json
from datetime import datetime
import threading
from credentials import BLOCKED_EXE, REPORT_DIR, WHITELIST_JSON
from write_report import write_report


logged_allowed_processes = set()

# Load whitelisted installers
def load_whitelisted_processes(json_file=WHITELIST_JSON):
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
            return set(proc.lower() for proc in data.get("WHITELISTED_PROCESSES", []))
    except Exception as e:
        print(f"[ERROR] Failed to load whitelist: {e}")
        return set()

WHITELISTED_PROCESSES = load_whitelisted_processes()

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        print(f"[KILLED] Process tree with PID {pid}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not kill PID {pid}: {e}")
        return False

def monitor_install_attempts():
    print(f"[MONITOR] Watching for installers...")
    while True:
        if not monitoring_enabled:
            time.sleep(1)
            continue

        for process in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_name = process.info['name'].lower()
                pid = process.info['pid']

                if any(installer in process_name for installer in BLOCKED_EXE):
                    if any(white in process_name for white in WHITELISTED_PROCESSES):
                        if process_name not in logged_allowed_processes:
                            write_install_log(f"Installer/Uninstaller allowed (whitelisted): {process_name}")
                            logged_allowed_processes.add(process_name)
                        continue  # Skip to next process

                    # Block unauthorized installer
                    write_install_log(f"[BLOCKED] Unauthorized installation/uninstallation attempt: {process_name}")
                    print(f"[BLOCKED] {process_name} (PID: {pid})")

                    success = kill_process_tree(pid)
                    if success:
                        write_install_log(f"[ACTION] {process_name} killed successfully.")
                    else:
                        write_install_log(f"[ERROR] Failed to kill {process_name}")

                    # Show alert to user
                    show_blocked_alert(process_name)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        time.sleep(0.5)

# Clean up logged processes not running anymore
running_processes = {p.info['name'].lower() for p in psutil.process_iter(attrs=['name'])}
logged_allowed_processes.intersection_update(running_processes)

def show_blocked_alert(process_name):
    print(
        "Installation Blocked",
        f"The installer '{process_name}' is not authorized.\nPlease contact your administrator."
    )

# Enable/Disable Monitoring
monitoring_enabled = True
monitoring_thread_started = False

def enable_install_uninstall_monitoring():
    global monitoring_enabled, monitoring_thread_started
    monitoring_enabled = True
    write_install_log("") # Blank line
    write_install_log("[MONITOR] Installer monitoring ENABLED")

    if not monitoring_thread_started:
        thread = threading.Thread(target=monitor_install_attempts, daemon=True)
        thread.start()
        monitoring_thread_started = True
        write_install_log("[THREAD] Installer monitoring thread started")

def disable_install_uninstall_monitoring():
    global monitoring_enabled
    monitoring_enabled = False
    print("Installer monitoring DISABLED")
    write_install_log("[MONITOR] Installer monitoring DISABLED")
    write_install_log("") # Blank line

def write_install_log(message):
    write_report(
        directory=REPORT_DIR,
        base_filename="install-uninstall",
        content=message,
        title="Install_Uninstall Reports"
    )

if __name__ == "__main__":
    enable_install_uninstall_monitoring()
    time.sleep(20)
    disable_install_uninstall_monitoring()