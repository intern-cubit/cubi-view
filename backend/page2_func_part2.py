import ctypes
import subprocess
import os
import json
import time
import winreg
import threading
from pathlib import Path
import keyboard


# ---------------- Registry Helpers ----------------
def set_reg_value(root, path, name, value, type=winreg.REG_DWORD):
    try:
        key = winreg.CreateKey(root, path)
        winreg.SetValueEx(key, name, 0, type, value)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error setting registry: {e}")

def del_reg_value(root, path, name):
    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

# ---------------- Feature 1: Screen Capture ----------------
def enable_screen_capture_block():
    set_reg_value(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "NoScreenCapture", 1)
    set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\SnippingTool.exe", "Debugger", "taskkill /f /im SnippingTool.exe", winreg.REG_SZ)
    set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\mspaint.exe", "Debugger", "taskkill /f /im mspaint.exe", winreg.REG_SZ)
    set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout", "Scancode Map", \
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x37\xE0\x00\x00\x00\x00\x00\x00")
    print("✅ Screen capture, PrintScreen and Paint disabled")

def disable_screen_capture_block():
    del_reg_value(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "NoScreenCapture")
    del_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\SnippingTool.exe", "Debugger")
    del_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\mspaint.exe", "Debugger")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, "Scancode Map")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    print("✅ Screen capture, PrintScreen and Paint re-enabled")

# ---------------- Feature 2: Block Ctrl+P and PrintScreen ----------------

# Global control variable
_keyblock_thread = None
_stop_keyblock = False

def start_keyblock_thread():
    global _keyblock_thread, _stop_keyblock
    _stop_keyblock = False

    def block_keys():
        while not _stop_keyblock:
            if keyboard.is_pressed('ctrl') and keyboard.is_pressed('p'):
                print("🔒 Ctrl+P blocked")
                keyboard.block_key('p')
                time.sleep(1)
            if keyboard.is_pressed('print_screen'):
                print("🔒 Print Screen blocked")
                keyboard.block_key('print_screen')
                time.sleep(1)
    
    _keyblock_thread = threading.Thread(target=block_keys, daemon=True)
    _keyblock_thread.start()

def stop_keyblock_thread():
    global _stop_keyblock
    _stop_keyblock = True
    # Unblock the keys
    keyboard.unblock_key('p')
    keyboard.unblock_key('print_screen')
    print("🔓 Ctrl+P and Print Screen unblocked")


# ---------------- Feature 3: Browser Print ----------------
def enable_browser_print_block():
    paths = {
        "Chrome": r"SOFTWARE\\Policies\\Google\\Chrome",
        "Edge": r"SOFTWARE\\Policies\\Microsoft\\Edge",
        "Brave": r"SOFTWARE\\Policies\\BraveSoftware\\Brave"
    }
    for browser, path in paths.items():
        set_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "PrintingEnabled", 0)
        set_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "CtrlPDisabled", 1)
        print(f"✅ {browser}: Print and Save as PDF disabled")

def disable_browser_print_block():
    paths = {
        "Chrome": r"SOFTWARE\\Policies\\Google\\Chrome",
        "Edge": r"SOFTWARE\\Policies\\Microsoft\\Edge",
        "Brave": r"SOFTWARE\\Policies\\BraveSoftware\\Brave"
    }
    for browser, path in paths.items():
        del_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "PrintingEnabled")
        del_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "CtrlPDisabled")
        print(f"✅ {browser}: Print and Save as PDF re-enabled")

# ---------------- Feature 4: Browser Downloads ----------------
def enable_download_block():
    chromium_paths = {
        "Chrome": r"SOFTWARE\\Policies\\Google\\Chrome",
        "Edge": r"SOFTWARE\\Policies\\Microsoft\\Edge",
        "Brave": r"SOFTWARE\\Policies\\BraveSoftware\\Brave",
        "Opera": r"SOFTWARE\\Policies\\Opera Software\\Opera"
    }
    for browser, path in chromium_paths.items():
        set_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "DownloadRestrictions", 3)
        set_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "AllowFileSelectionDialogs", 0)
        print(f"✅ {browser}: Downloads disabled")

    policy_folder = Path(os.getenv("PROGRAMFILES")) / "Mozilla Firefox" / "distribution"
    policy_path = policy_folder / "policies.json"
    policy_folder.mkdir(parents=True, exist_ok=True)
    policy = {
        "policies": {
            "DownloadRestrictions": {
                "BlockedSchemes": ["http", "https", "ftp"]
            }
        }
    }
    with open(policy_path, "w") as f:
        json.dump(policy, f, indent=4)
    print("✅ Firefox: Downloads disabled")

def disable_download_block():
    chromium_paths = {
        "Chrome": r"SOFTWARE\\Policies\\Google\\Chrome",
        "Edge": r"SOFTWARE\\Policies\\Microsoft\\Edge",
        "Brave": r"SOFTWARE\\Policies\\BraveSoftware\\Brave",
        "Opera": r"SOFTWARE\\Policies\\Opera Software\\Opera"
    }
    for browser, path in chromium_paths.items():
        del_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "DownloadRestrictions")
        del_reg_value(winreg.HKEY_LOCAL_MACHINE, path, "AllowFileSelectionDialogs")
        print(f"✅ {browser}: Downloads re-enabled")

    policy_path = Path(os.getenv("PROGRAMFILES")) / "Mozilla Firefox" / "distribution" / "policies.json"
    if policy_path.exists():
        os.remove(policy_path)
        print("✅ Firefox: Download policy removed")

# ---------------- Feature 5: PDF Printer ----------------
def disable_pdf_printer():
    try:
        subprocess.run(['powershell', '-Command', 'Disable-Printer -Name "Microsoft Print to PDF"'], check=True)
        print("✅ Microsoft Print to PDF disabled")
    except Exception as e:
        print(f"Error disabling PDF printer: {e}")

def enable_pdf_printer():
    try:
        subprocess.run(['powershell', '-Command', 'Enable-Printer -Name "Microsoft Print to PDF"'], check=True)
        print("✅ Microsoft Print to PDF re-enabled")
    except Exception as e:
        print(f"Error enabling PDF printer: {e}")


def enable_printer_block():
    enable_browser_print_block()
    disable_pdf_printer()
    start_keyblock_thread()

def disable_printer_block():
    disable_browser_print_block()
    enable_pdf_printer()
    stop_keyblock_thread()

