import time
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import json
import time
import os

from credentials import CONFIG_PATH
from page1_func_part1 import (enable_activity_tracker, disable_activity_tracker,
                                     enable_mouse_movement_tracker,disable_mouse_movement_tracker,
                                     enable_mouse_click_tracker, disable_mouse_click_tracker,
                                     enable_print_job_tracking, disable_print_job_tracking,
                                     enable_screen_lock_monitoring, async_disable_screen_lock_monitoring,
                                     enable_location_tracking, disable_location_tracking)
from page1_func_part2 import (enable_keylogger, disable_keylogger, 
                       enable_keystroke_counter, disable_keystroke_counter,
                       enable_screenshot_capture, disable_screenshot_capture, 
                       enable_browser_tracking, disable_browser_tracking,
                       enable_application_tracking, disable_application_tracking,
                       enable_clipboard_monitoring, disable_clipboard_monitoring)
from page1_func_part3 import (enable_audio_capture, disable_audio_capture, enable_video_capture, disable_video_capture)
from monitor_installs import enable_install_uninstall_monitoring, disable_install_uninstall_monitoring
from prevent_vpn import enable_vpn_monitoring, disable_vpn_monitoring
from page2_func_part1 import (enable_incognito_blocking, disable_incognito_blocking, block_extensions, 
                              unblock_extensions,enable_website_whitelist, disable_website_whitelist,
                              enable_website_blocking, disable_website_blocking)
from page2_func_part2 import (enable_printer_block, disable_printer_block,  
                              enable_download_block, disable_download_block,
                              enable_screen_capture_block,disable_screen_capture_block)
from page2_func_part3 import (enable_usb_ports, disable_usb_ports, enable_lunch_mode_monitor, disable_lunch_mode_monitor)

from shutdown_detection import run_schedule,handle_shutdown_event

# Wrapper functions for auto-confirmed actions (for monitoring system)
def auto_enable_incognito_blocking():
    return enable_incognito_blocking(confirmed=True)

def auto_disable_incognito_blocking():
    return disable_incognito_blocking(confirmed=True)

def auto_block_extensions():
    return block_extensions(confirmed=True)

def auto_unblock_extensions():
    return unblock_extensions(confirmed=True)

def auto_enable_vpn_monitoring():
    return enable_vpn_monitoring(confirmed=True)

def auto_disable_vpn_monitoring():
    return disable_vpn_monitoring(confirmed=True)

    # Create threads
schedule_thread = threading.Thread(target=run_schedule, name="DailyScheduler", daemon=True)
shutdown_thread = threading.Thread(target=handle_shutdown_event, name="ShutdownMonitor", daemon=True) 


def not_implemented():
    print("Feature Not Yet Deployed", "This feature is under development.")

enable_funcs = {
    ##################### Functions for Page 1 ########################
    "Keylogger": enable_keylogger,
    "Keystroke / Word Count": enable_keystroke_counter,
    "Clipboard Monitoring": enable_clipboard_monitoring,
    "Mouse Movement Tracking":enable_mouse_movement_tracker,
    "Mouse Click Count": enable_mouse_click_tracker,
    "Browser History Logging": enable_browser_tracking,
    "Capture Screenshots": enable_screenshot_capture,
    "Application Usage Tracking": enable_application_tracking,
    "Capture Audio Clips": enable_audio_capture,
    "Installation / Uninstallation Logs": enable_install_uninstall_monitoring,
    "Capture Video Clips": enable_video_capture,
    "Print Job Monitoring": enable_print_job_tracking,
    "Active/Idle Time Detection": enable_activity_tracker,
    "Laptop Geolocation (IP/GPS Based)": enable_location_tracking,
    "Detect Login / Logout + Screen Lock / Unlock":enable_screen_lock_monitoring,
    ##################### Functions for Page 2 ########################
    "VPN Detection & Blocking" : auto_enable_vpn_monitoring, 
    "Chrome Extension Restrictions" : auto_block_extensions,
    "USB Port Access Control" : disable_usb_ports, 
    "Incognito Mode Blocking" : auto_enable_incognito_blocking,
    "Website Whitelisting" : enable_website_whitelist,
    "Website Blocking" : enable_website_blocking,
    "Screenshot / Snipping Tool Prevention" : enable_screen_capture_block,
    "Block print" : enable_printer_block,
    "Copy-Paste Enable / Disable" : not_implemented,
    "Download Enable / Disable" : enable_download_block,
    "Built-in Ad Blocker" : not_implemented, 
    "Custom Antivirus & Spam Link Detection" : not_implemented,
    "Internet / Screen Time Limits" : not_implemented, 
    "Lunch Break Mode" : enable_lunch_mode_monitor
}

disable_funcs = {
    ##################### Functions for Page 1 ########################
    "Keylogger": disable_keylogger,
    "Clipboard Monitoring": disable_clipboard_monitoring,
    "Mouse Movement Tracking": disable_mouse_movement_tracker,
    "Browser History Logging": disable_browser_tracking,
    "Capture Screenshots": disable_screenshot_capture,
    "Application Usage Tracking": disable_application_tracking,
    "Capture Audio Clips": disable_audio_capture,
    "Installation / Uninstallation Logs": disable_install_uninstall_monitoring,
    "Capture Video Clips": disable_video_capture,
    "Print Job Monitoring": disable_print_job_tracking,
    "Active/Idle Time Detection": disable_activity_tracker,
    "Laptop Geolocation (IP/GPS Based)": disable_location_tracking,
    "Mouse Click Count": disable_mouse_click_tracker,
    "Keystroke / Word Count": disable_keystroke_counter,
    "Detect Login / Logout + Screen Lock / Unlock": async_disable_screen_lock_monitoring,
    ##################### Functions for Page 2 ########################
    "VPN Detection & Blocking" : auto_disable_vpn_monitoring, 
    "Chrome Extension Restrictions" : auto_unblock_extensions,
    "USB Port Access Control" : enable_usb_ports, 
    "Incognito Mode Blocking" : auto_disable_incognito_blocking,
    "Website Whitelisting" : disable_website_whitelist, 
    "Website Blocking" : disable_website_blocking,
    "Screenshot / Snipping Tool Prevention" : disable_screen_capture_block,
    "Block print" : disable_printer_block,
    "Copy-Paste Enable / Disable" : not_implemented,
    "Download Enable / Disable" : disable_download_block,
    "Built-in Ad Blocker" : not_implemented, 
    "Custom Antivirus & Spam Link Detection" : not_implemented,
    # "Internet / Screen Time Limits" : not_implemented, 
    "Lunch Break Mode" : disable_lunch_mode_monitor
}

last_config = {}
running_flags = {}

class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(CONFIG_PATH):
            print("[Watchdog] Config file changed, updating...")
            apply_config_changes()

def apply_config_changes():
    global last_config

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

        for feature, enabled in config.items():
            was_enabled = last_config.get(feature, False)

            if enabled and not was_enabled and feature in enable_funcs:
                enable_funcs[feature]()
                running_flags[feature] = True
                print("Enabled Function:", feature)

            elif not enabled and was_enabled and feature in disable_funcs:
                disable_funcs[feature]()
                running_flags.pop(feature, None)
                print("Disabled Function:", feature)

        last_config = config
    except Exception as e:
        print(f"[!] Error applying config changes: {e}")

def start_watch_config():
    event_handler = ConfigChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(CONFIG_PATH)), recursive=False)
    observer.start()
    print("[+] Watching monitor_config.json for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def start_main():
    print("[+] Starting Cubi-View monitoring threads...")
    # Start threads
    schedule_thread.start()
    shutdown_thread.start()

    print("[*] Applying config at startup...")
    apply_config_changes()   # <-- this ensures features already enabled in config.json start immediately

    print("[*] Monitoring config for feature toggles...")
    start_watch_config()  # Keep watching for further changes


