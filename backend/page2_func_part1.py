# This script contains functions for Enabling and disabling Incognito in Browsers, 
# block or unblock chrome extensions, 
# whitelist websites
# Block Websites

import os
import json
import winreg
import subprocess
import psutil
from pathlib import Path
import datetime
from tkinter import messagebox

from write_report import write_report
from credentials import REPORT_DIR, WHITELIST_FILE, BLOCKLIST_FILE

# Supported Chromium browsers and their registry paths
CHROMIUM_BROWSERS = {
    "Chrome": r"SOFTWARE\Policies\Google\Chrome",
    "Edge": r"SOFTWARE\Policies\Microsoft\Edge",
    "Brave": r"SOFTWARE\Policies\BraveSoftware\Brave",
    "Opera": r"SOFTWARE\Policies\Opera Software\Opera"
}

# Process names for killing browsers
BROWSER_PROCESSES = [
    "chrome.exe", "msedge.exe", "brave.exe", "opera.exe", "firefox.exe"
]

# REPORT_DIR = "reports"
# REPORT_DIR_Extensions = os.path.join(REPORT_DIR, "ChromeExtension_reports")
# os.makedirs(REPORT_DIR_Extensions, exist_ok=True)

# REPORT_DIR_Incognito = os.path.join(REPORT_DIR, "Incognito_reports")
# os.makedirs(REPORT_DIR_Incognito, exist_ok=True)

# def log_action(action: str, Directory):
#     """Log action with timestamp into a daily report file"""
#     now = datetime.datetime.now()
#     timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
#     filename = f"Incognito_{now.strftime('%d-%m-%Y')}.txt"
#     report_path = os.path.join(Directory, filename)
#     with open(report_path, "a", encoding="utf-8") as f:
#         f.write(f"[{timestamp}] {action}\n")
#     print(f"[{timestamp}] {action}")

def log_incognito_action(action: str):
    write_report(
        directory= REPORT_DIR,
        base_filename="Incognito_reports",
        content=action,
        title= "Incognito report"
    )

def log_chrome_ext(action: str):
    write_report(
                directory=REPORT_DIR,
                base_filename="Chrome_extension_report",
                content=action,
                title="Chrome Extension Report"
            )

def set_chromium_registry(browser, allow):
    try:
        path = CHROMIUM_BROWSERS[browser]
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            value = 0 if allow else 1
            winreg.SetValueEx(key, "IncognitoModeAvailability", 0, winreg.REG_DWORD, value)
        log_incognito_action(f"{browser}: {'Enabled' if allow else 'Disabled'} Incognito Mode.")
    except Exception as e:
        log_incognito_action(f"{browser}: Registry update failed - {e}")


def set_firefox_policy(allow):
    try:
        policy_folder = Path(os.getenv("PROGRAMFILES")) / "Mozilla Firefox" / "distribution"
        policy_path = policy_folder / "policies.json"

        if allow:
            if policy_path.exists():
                policy_path.unlink()
            print("Firefox: Enabled Private Browsing")
            log_incognito_action("Firefox: Enabled Private Browsing")
        else:
            policy_folder.mkdir(parents=True, exist_ok=True)
            data = {"policies": {"DisablePrivateBrowsing": True}}
            with open(policy_path, 'w') as f:
                json.dump(data, f, indent=4)
            print("Firefox: Disabled Private Browsing")
            log_incognito_action("Firefox: Disabled Private Browsing")
    except Exception as e:
        print(f"Firefox: Failed to update policy: {e}")
        log_incognito_action(f"Firefox: Policy update failed - {e}")

def close_browsers():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() in BROWSER_PROCESSES:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"Closed {proc.info['name']}")
                log_incognito_action(f"Closed browser: {proc.info['name']}")
            except Exception:
                print(f"Could not close {proc.info['name']}")
                log_incognito_action(f"Could not close browser: {proc.info['name']}")


# Optional: Define restart logic (commented by default)
def restart_browsers():
    browser_paths = {
        "chrome.exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "msedge.exe": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "brave.exe": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "opera.exe": r"C:\Users\%USERNAME%\AppData\Local\Programs\Opera\launcher.exe",
        "firefox.exe": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    }
    for exe, path in browser_paths.items():
        if os.path.exists(path):
            subprocess.Popen(path)
            print(f"Restarted {exe}")
            log_incognito_action(f"Restarted {exe}")


def enable_incognito_blocking():
    choice = messagebox.askyesno("CubiView", "This will close all the Browsers. Do you want to continue?")
    if choice == True:
        close_browsers()
        for browser in CHROMIUM_BROWSERS:
            set_chromium_registry(browser, allow=False)
        set_firefox_policy(allow=False)
        print("Incognito/Private mode DISABLED for all supported browsers.")
        log_incognito_action("Incognito/Private mode DISABLED for all supported browsers.")
        restart_browsers()
    else:
        messagebox.showinfo("CubiView","Incognito mode not enabled")

def disable_incognito_blocking():
    close_browsers()
    for browser in CHROMIUM_BROWSERS:
        set_chromium_registry(browser, allow=True)
    set_firefox_policy(allow=True)
    print("Incognito/Private mode ENABLED for all supported browsers.")
    log_incognito_action("Incognito/Private mode ENABLED for all supported browsers.")
    restart_browsers()

####################### Block / Unblock Chrome Extensions ################################

# Block all chrome extensions
def block_extensions():
    subprocess.run("reg add HKLM\\Software\\Policies\\Google\\Chrome\\ExtensionInstallBlocklist /v 1 /t REG_SZ /d * /f", shell=True)
    log_chrome_ext(f" Blocked all Chrome Extenstions")
    close_browsers()
    restart_browsers()

#Unblock all chrome extensions
def unblock_extensions():
    subprocess.run("reg delete HKLM\\Software\\Policies\\Google\\Chrome\\ExtensionInstallBlocklist /f", shell=True)
    log_chrome_ext(f" Unblocked all Chrome Extenstions")
    close_browsers()
    restart_browsers()


##################### Whitelist websites #################

PROXY_SERVER = "127.0.0.1:5000"

# WHITELIST_FILE = "whitelist_sites.json"

# Ensure file exists
if not os.path.exists(WHITELIST_FILE):
    with open(WHITELIST_FILE, "w") as f:
        json.dump([], f)

def load_whitelist_sites():
    with open(WHITELIST_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_whitelist_sites(websites):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(websites, f, indent=4)


# def format_proxy_exceptions(sites):
#     return ";".join([f"*.{site}" for site in sites] + ["localhost", "<local>"])
def format_proxy_exceptions(sites):
    """
    Ensures both root and wildcarded subdomains are excluded from proxy
    Example: ['chatgpt.com'] → ['chatgpt.com', '*.chatgpt.com']
    """
    exceptions = []
    for site in sites:
        site = site.strip().lower()
        exceptions.append(site)
        if not site.startswith("*."):
            exceptions.append(f"*.{site}")
    exceptions += ["localhost", "<local>"]
    return ";".join(exceptions)


def enable_website_whitelist():
    sites = load_whitelist_sites()
    exceptions = format_proxy_exceptions(sites)
    key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, "ProxyServer", 0, winreg.REG_SZ, PROXY_SERVER)
        winreg.SetValueEx(k, "ProxyOverride", 0, winreg.REG_SZ, exceptions)

def disable_website_whitelist():
    key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        try:
            winreg.DeleteValue(k, "ProxyServer")
            winreg.DeleteValue(k, "ProxyOverride")
            generate_website_whitelist_report()
        except FileNotFoundError:
            pass


def is_proxy_enabled():
    """Check if proxy is currently enabled in registry."""
    key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            value, regtype = winreg.QueryValueEx(k, "ProxyEnable")
            return value == 1
    except FileNotFoundError:
        return False

def generate_website_whitelist_report():
    sites = load_whitelist_sites()
    proxy_status = "ENABLED" if is_proxy_enabled() else "DISABLED"

    content = [
        "",  # spacing
        f"Website Whitelist Report",
        f"Proxy Server: {PROXY_SERVER}",
        f"Whitelist Status: {proxy_status}",
        f"Total Whitelisted Sites: {len(sites)}",
        "",  # spacing
        "Whitelisted Websites:"
    ] + [f" - {site}" for site in sites]

    write_report(
        directory=REPORT_DIR,  # or use REPORT_DIR if defined elsewhere
        base_filename="website_whitelist_report",
        content=content,
        title="Website Whitelist Report"
    )


############ Block websites ################
import os
import json
import ctypes
import threading

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BLOCK_TAG = "# blocked by Python"
REDIRECT_IP = "127.0.0.1"
# BLOCKLIST_FILE = "blocklist_sites.json"


def load_blocked_sites():
    """Load the list of websites to block from a JSON file."""
    if not os.path.exists(BLOCKLIST_FILE):
        return []
    with open(BLOCKLIST_FILE, 'r') as f:
        try:
            data = json.load(f)
            return data.get("websites", [])
        except json.JSONDecodeError:
            return []


def block_sites():
    """Add entries to the hosts file to block specified websites."""
    sites = load_blocked_sites()
    if not sites:
        return

    with open(HOSTS_PATH, "r+", encoding="utf-8") as file:
        content = file.read()
        for site in sites:
            entry = f"{REDIRECT_IP} {site} {BLOCK_TAG}\n"
            if site not in content:
                file.write(entry)


def unblock_sites():
    """Remove blocked websites entries from the hosts file."""
    if not os.path.exists(HOSTS_PATH):
        return

    with open(HOSTS_PATH, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(HOSTS_PATH, "w", encoding="utf-8") as file:
        for line in lines:
            if BLOCK_TAG not in line:
                file.write(line)

    generate_blocked_websites_report()


def enable_website_blocking():
    thread = threading.Thread(target=_enable_website_blocking_logic)
    thread.start()


def _enable_website_blocking_logic():
    block_sites()
    generate_blocked_websites_report()


def disable_website_blocking():
    unblock_sites()


def generate_blocked_websites_report():
    sites = load_blocked_sites()
    block_status = "ENABLED" if is_block_active() else "DISABLED"

    content = [
        "",
        "Website Blocking Report",
        f"Block Status: {block_status}",
        f"Total Blocked Sites: {len(sites)}",
        "",
        "Blocked Websites:"
    ] + [f" - {site}" for site in sites]

    write_report(
        directory=REPORT_DIR,
        base_filename="blocked_websites_report",
        content=content,
        title="Blocked Websites Report"
    )


def is_block_active():
    """Check if any blocked website entries exist in the hosts file."""
    if not os.path.exists(HOSTS_PATH):
        return False
    with open(HOSTS_PATH, "r", encoding="utf-8") as file:
        content = file.read()
        return BLOCK_TAG in content
