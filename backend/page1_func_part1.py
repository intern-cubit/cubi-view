# This script contains functions for Active and Idle time tracking, 
# Mouse movement tracking, 
# mouse clicks tracking 
# Print job monitoring, 
# screen lock / unlock  
# geolocation tracking

from pynput import mouse, keyboard
import time
import threading
#import signal
#import sys
import os
from datetime import datetime
import win32print
import win32api
import requests
import os
import win32con
import win32gui
import win32ts
import win32api
import win32process
import win32event
import win32com.client

from write_report import write_report
from credentials import REPORT_DIR


# Configuration
IDLE_THRESHOLD = 60
# REPORT_DIR = "reports"
# os.makedirs(REPORT_DIR, exist_ok=True)

# Global variables
last_active_time = time.time()
total_active_time = 0
total_idle_time = 0
mouse_movement_count = 0
mouse_click_count = 0
print_job_tracking = False
print_job_listener_thread = None
print_jobs = []
mouse_tracking_start_time = None
mouse_tracking_end_time = None
mouse_click_tracking_start_time = None 
mouse_click_tracking_end_time =  None
mouse_movements = []  # Stores tuples: (timestamp, x, y)
mouse_clicks = []     # Stores tuples: (timestamp, x, y, button, pressed)
# Screen lock vars
screen_lock_data = []
screen_lock_running = False
screen_lock_thread = None
screen_lock_listener = None
screen_lock_running = False
screen_lock_thread = None

# Manually define these constants
WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8


# States
activity_running = False
mouse_move_running = False
mouse_click_running = False

# Thread and Listener references
activity_thread = None
keyboard_listener = None
mouse_listener = None
lock = threading.Lock()

# ========== Event Handlers ==========
def on_activity():
    global last_active_time
    with lock:
        last_active_time = time.time()

def on_key_press(key):
    if activity_running:
        on_activity()

def on_mouse_move(x, y):
    global mouse_movement_count
    if mouse_move_running:
        with lock:
            mouse_movement_count += 1
            mouse_movements.append((time.time(), x, y))
    if activity_running:
        on_activity()

def on_mouse_click(x, y, button, pressed):
    global mouse_click_count
    if pressed and mouse_click_running:
        with lock:
            mouse_click_count += 1
            mouse_clicks.append((time.time(), x, y, button, pressed))
    if activity_running:
        on_activity()


def on_mouse_scroll(x, y, dx, dy):
    if activity_running:
        on_activity()

# ========== Trackers ==========
def monitor_activity():
    global total_active_time, total_idle_time
    while activity_running:
        time.sleep(1)
        now = time.time()
        with lock:
            if now - last_active_time <= 1:
                total_active_time += 1
            else:
                total_idle_time += 1

# ========== Enable Functions ==========
def enable_activity_tracker():
    global activity_running, activity_thread, keyboard_listener
    if activity_running:
        print("Activity tracker already running.")
        return
    activity_running = True
    print("[+] Activity Tracker Enabled")

    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.start()

    activity_thread = threading.Thread(target=monitor_activity)
    activity_thread.daemon = True
    activity_thread.start()

def enable_mouse_movement_tracker():
    global mouse_move_running, mouse_listener
    if mouse_move_running:
        print("Mouse movement tracker already running.")
        return
    mouse_move_running = True
    print("[+] Mouse Movement Tracker Enabled")

    if not mouse_listener:
        mouse_listener = mouse.Listener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll
        )
        mouse_listener.start()

def enable_mouse_click_tracker():
    global mouse_click_running, mouse_listener
    if mouse_click_running:
        print("Mouse click tracker already running.")
        return
    mouse_click_running = True
    print("[+] Mouse Click Tracker Enabled")

    if not mouse_listener:
        mouse_listener = mouse.Listener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll
        )
        mouse_listener.start()

# ========== Disable Functions ==========
def disable_activity_tracker():
    global activity_running
    if not activity_running:
        print("Activity tracker not running.")
        return
    activity_running = False
    time.sleep(1)
    print("[-] Activity Tracker Disabled")
    if keyboard_listener:
        keyboard_listener.stop()
    generate_activity_report()

def disable_mouse_movement_tracker():
    global mouse_move_running
    global mouse_movements
    if not mouse_move_running:
        print("Mouse movement tracker not running.")
        return
    mouse_move_running = False
    print("[-] Mouse Movement Tracker Disabled")
    generate_mouse_movement_report()

def disable_mouse_click_tracker():
    global mouse_clicks
    global mouse_click_running
    if not mouse_click_running:
        print("Mouse click tracker not running.")
        return
    mouse_click_running = False
    print("[-] Mouse Click Tracker Disabled")
    generate_mouse_click_report()

# ========== Report Generators ==========


def generate_activity_report():
    total_time = total_active_time + total_idle_time
    summary = [
        f"Total Time   : {int(total_time)} seconds",
        f"Working Time : {int(total_active_time)} seconds",
        f"Idle Time    : {int(total_idle_time)} seconds"
    ]
    write_report(
        directory=REPORT_DIR,
        base_filename="activity_report",
        content=summary,
        title="--- Active vs Idle Time Report ---",
        with_timestamp=False,
    )

def generate_mouse_movement_report():
    lines = [
        f"Date        : {mouse_tracking_start_time.strftime('%Y-%m-%d')}" if mouse_tracking_start_time else "Date        : Unknown",
        f"Start Time  : {mouse_tracking_start_time.strftime('%H:%M:%S')}" if mouse_tracking_start_time else "Start Time  : Unknown",
        f"End Time    : {mouse_tracking_end_time.strftime('%H:%M:%S')}" if mouse_tracking_end_time else "End Time    : Unknown",
        f"Total Moves : {len(mouse_movements)}",
        "=" * 50 + "\n"
    ]

    for timestamp, x, y in mouse_movements:
        ts = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"[{ts}] Moved to ({x}, {y})")

    write_report(
        directory=REPORT_DIR,
        base_filename="mouse_movement_report",
        content=lines,
        title="Mouse Movement Report",
        with_timestamp=False
    )


def generate_mouse_click_report():
    lines = [
        f"Date        : {mouse_click_tracking_start_time.strftime('%Y-%m-%d')}" if mouse_click_tracking_start_time else "Date        : Unknown",
        f"Start Time  : {mouse_click_tracking_start_time.strftime('%H:%M:%S')}" if mouse_click_tracking_start_time else "Start Time  : Unknown",
        f"End Time    : {mouse_click_tracking_end_time.strftime('%H:%M:%S')}" if mouse_click_tracking_end_time else "End Time    : Unknown",
        f"Total Clicks: {len(mouse_clicks)}",
        "=" * 50 + "\n"
    ]

    for entry in mouse_clicks:
        if len(entry) >= 3:
            ts, button, pos = entry[:3]
            timestamp = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"[{timestamp}] {button} click at {pos}")
        else:
            print("Malformed mouse click entry:", entry)

    write_report(
        directory=REPORT_DIR,
        base_filename="mouse_click_report",
        content=lines,
        title="Mouse Click Report",
        with_timestamp=False
    )



# ======================================Print Job monitoring============================================#
# Function to log print job details
# def log_print_job(printer_name, document_name, user_name):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     job_details = {
#         'timestamp': timestamp,
#         'printer': printer_name,
#         'document': document_name,
#         'user': user_name
#     }
#     print_jobs.append(job_details)

#     # Write to a report file
#     report_file = os.path.join(REPORT_DIR, "print_job_report.txt")
#     with open(report_file, 'a', encoding='utf-8') as f:
#         f.write(f"Timestamp: {timestamp}, Printer: {printer_name}, Document: {document_name}, User: {user_name}\n")

def log_print_job(printer_name, document_name, user_name):
    content = f"Printer: {printer_name}, Document: {document_name}, User: {user_name}"
    write_report(
        directory=REPORT_DIR,
        base_filename="print_job_report",
        content=content
    )


# Function to track print jobs
def track_print_jobs():
    global print_jobs
    last_checked_jobs = {}
    
    while print_job_tracking:
        # Get all printers
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        
        for printer in printers:
            printer_name = printer[2]
            
            # Get print job info for each printer
            try:
                hPrinter = win32print.OpenPrinter(printer_name)
                job_info = win32print.EnumJobs(hPrinter, 0, 100, 1)  # Get up to 100 jobs
                for job in job_info:
                    job_id = job["JobId"]
                    if job_id not in last_checked_jobs:
                        document_name = job["pDocument"]
                        user_name = job["pUserName"]
                        log_print_job(printer_name, document_name, user_name)
                        last_checked_jobs[job_id] = True
                win32print.ClosePrinter(hPrinter)
            except Exception as e:
                print(f"Error accessing printer {printer_name}: {e}")
        
        time.sleep(5)  # Sleep for 5 seconds before checking again

# Enable function for print job tracking
def enable_print_job_tracking():
    global print_job_tracking, print_job_listener_thread
    if print_job_tracking:
        print("Print job tracking is already running.")
        return

    print_job_tracking = True
    print("[+] Print Job Tracking Started")

    print_job_listener_thread = threading.Thread(target=track_print_jobs)
    print_job_listener_thread.daemon = True
    print_job_listener_thread.start()

def disable_print_job_tracking():
    global print_job_tracking, print_job_listener_thread
    if not print_job_tracking:
        print("Print job tracking is not active.")
        return

    print("[-] Stopping Print Job Tracking...")
    print_job_tracking = False

    if print_job_listener_thread is not None:
        print_job_listener_thread.join()
        print_job_listener_thread = None

    print("[-] Print Job Tracking Stopped")



# ===================== Screen Lock / Unlock Tracking ==================
screen_lock_stop_event = threading.Event()

class SessionChangeListener:
    def __init__(self):
        self.className = "SessionChangeListenerWindow"
        self.hInstance = win32api.GetModuleHandle(None)
        self._register_window_class()
        self.hwnd = self._create_window()
        win32ts.WTSRegisterSessionNotification(self.hwnd, win32ts.NOTIFY_FOR_THIS_SESSION)

    def _register_window_class(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = self.className
        win32gui.RegisterClass(wc)

    def _create_window(self):
        return win32gui.CreateWindow(
            self.className,
            self.className,
            0,
            0, 0, 0, 0,
            0, 0, self.hInstance, None
        )

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_WTSSESSION_CHANGE:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if wparam == WTS_SESSION_LOCK:
                screen_lock_data.append({'timestamp': timestamp, 'state': 'Locked'})
                print(f"[{timestamp}] Screen Locked")
            elif wparam == WTS_SESSION_UNLOCK:
                screen_lock_data.append({'timestamp': timestamp, 'state': 'Unlocked'})
                print(f"[{timestamp}] Screen Unlocked")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def run(self):
        while not screen_lock_stop_event.is_set():
            win32gui.PumpWaitingMessages()
            time.sleep(0.1)


    def stop(self):
        win32ts.WTSUnRegisterSessionNotification(self.hwnd)
        screen_lock_stop_event.set()
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)



# Enable function
def enable_screen_lock_monitoring():
    global screen_lock_running, screen_lock_thread, screen_lock_listener
    if screen_lock_running:
        print("Screen lock monitoring already running.")
        return

    screen_lock_running = True
    print("[+] Screen Lock Monitoring Started")

    def run_listener():
        global screen_lock_listener
        screen_lock_listener = SessionChangeListener()
        screen_lock_listener.run()

    screen_lock_thread = threading.Thread(target=run_listener, daemon=True)
    screen_lock_thread.start()


def async_disable_screen_lock_monitoring():
    threading.Thread(target=disable_screen_lock_monitoring, daemon=True).start()

# Disable function with proper thread shutdown
def disable_screen_lock_monitoring():
    global screen_lock_running, screen_lock_listener, screen_lock_thread
    if not screen_lock_running:
        print("Screen lock monitoring not active.")
        return

    print("[-] Stopping Screen Lock Monitoring...")
    screen_lock_running = False

    if screen_lock_listener:
        screen_lock_listener.stop()
        screen_lock_listener = None

    if screen_lock_thread:
        screen_lock_thread.join(timeout=5)
        if screen_lock_thread.is_alive():
            print("[!] Warning: Screen lock thread did not terminate properly.")
        else:
            print("[+] Screen lock thread terminated successfully.")
        screen_lock_thread = None

    generate_screen_lock_report()


def generate_screen_lock_report():
    if not screen_lock_data:
        print("No screen lock/unlock data to report.")
        return

    content = [f"{entry['state']}" for entry in screen_lock_data]
    write_report(
        directory=REPORT_DIR,
        base_filename="screen_lock_report",
        content=content,
        title="Screen Lock/Unlock Activity Report"
    )



# ========================= Geolocating the laptop ===========================================

# Global toggle
location_tracking_running = False
location_tracking_start_time = None
location_tracking_end_time = None
location_data = {}


def get_location_info():
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[!] Error retrieving location: {e}")
    return {}


def generate_location_report():
    if not location_data:
        print("No location data to report.")
        return

    content = [
        f"{k.capitalize()}: {v}" for k, v in location_data.items()
    ]
    content.insert(0, f"Start Time: {location_tracking_start_time}, End Time: {location_tracking_end_time}")
    write_report(
        directory=REPORT_DIR,
        base_filename="location_report",
        content=content,
        title="Location Tracking Report"
    )


# ========= Enable / Disable Functions =========
def enable_location_tracking():
    global location_tracking_running, location_tracking_start_time, location_data
    if location_tracking_running:
        print("[!] Location tracking already enabled.")
        return
    location_tracking_running = True
    location_tracking_start_time = datetime.now()
    print("[+] Location tracking started.")
    location_data.update(get_location_info())

def disable_location_tracking():
    global location_tracking_running, location_tracking_end_time
    if not location_tracking_running:
        print("[!] Location tracking not active.")
        return
    location_tracking_running = False
    location_tracking_end_time = datetime.now()
    print("[-] Location tracking stopped.")
    generate_location_report()



# ========== Exit Handler ==========
#def exit_handler(signum=None, frame=None):
#    disable_activity_tracker()
#    disable_mouse_movement_tracker()
#    disable_mouse_click_tracker()
#    sys.exit(0)

#signal.signal(signal.SIGINT, exit_handler)
#signal.signal(signal.SIGTERM, exit_handler) 

if __name__ == "__main__":
    enable_screen_lock_monitoring()
    time.sleep(60)
    disable_screen_lock_monitoring()
