# GUI_backend.py

import subprocess
import psutil
import json
import os
import requests
from write_report import send_email_with_zip, load_smtp_credentials
from get_systemID import get_system_id
from credentials import (
    VERSION_URL, RELEASES_URL, ACTIVATION_PATH,
    LOCAL_VERSION_FILE, CONFIG_PATH, WHITELIST_FILE, BLOCKLIST_FILE,
    WHITELIST_JSON, USER_ID_PATH, SMTP_CREDENTIALS_FILE
)

# === CONFIG HANDLING ===
def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty dict if file not found or if it's invalid JSON
        return {}

def save_config(config):
    print("Saving configuration to", CONFIG_PATH)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        print("Configuration saved successfully.", config)
    except IOError as e:
        print(f"Error saving configuration: {e}")
        raise IOError(f"Failed to save configuration to {CONFIG_PATH}: {e}")

def toggle_feature(feature, enabled):
    config = load_config()

    if feature == "Website Whitelisting" and enabled:
        if config.get("Website Blocking"):
            config["Website Blocking"] = False
    elif feature == "Website Blocking" and enabled:
        if config.get("Website Whitelisting"):
            config["Website Whitelisting"] = False

    config[feature] = bool(enabled)
    save_config(config)


# === MONITORING CONTROL ===
def get_startup_folder():
    # Gets the current user's startup folder path
    return os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')

def start_monitoring():
    try:
        # Start activator.exe
        subprocess.Popen(["activator.exe"], shell=False)

        # Add activator.exe to startup
        startup_folder = get_startup_folder()
        shortcut_path = os.path.join(startup_folder, "Activator.lnk")
        
        # Create shortcut using PowerShell
        activator_path = os.path.abspath("activator.exe")
        powershell_script = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{activator_path}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(activator_path)}"
        $Shortcut.Save()
        '''
        subprocess.run(["powershell", "-Command", powershell_script], check=True)

        print("Activator added to startup.")
        return True
    except Exception as e:
        print(f"Error starting monitoring: {e}")
        return False

def stop_monitoring():
    try:
        # Kill activator.exe
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and proc.info['name'].lower() == 'activator.exe':
                proc.terminate()

        # Remove from startup folder
        startup_folder = get_startup_folder()
        shortcut_path = os.path.join(startup_folder, "Activator.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("Activator removed from startup.")
        return True
    except Exception as e:
        print(f"Error stopping monitoring: {e}")
        return False


def is_monitoring_running():
    return any(proc.info['name'].lower() == 'activator.exe' for proc in psutil.process_iter(['name']))

# === ACTIVATION KEY ===
def load_activation_key():
    if os.path.exists(ACTIVATION_PATH):
        try:
            with open(ACTIVATION_PATH, 'r') as f:
                data = json.load(f)
                return data.get("activationKey", "")
        except:
            return ""
    return ""

def save_activation_key(key):
    system_id = get_system_id()
    data = {"activationKey": key, "systemId": system_id}
    try:
        with open(ACTIVATION_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving activation key: {e}")
        return False

# === VERSION HANDLING ===
def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        try:
            with open(LOCAL_VERSION_FILE, "r") as f:
                return f.read().strip()
        except:
            return "Error reading version"
    return "Unknown"

def get_remote_version():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        return response.text.strip()
    except:
        return None

def perform_full_update(version):
    files_to_update = ["GUI.exe", "activator.exe"]
    success_files = []
    try:
        for exe in files_to_update:
            url = f"{RELEASES_URL}{exe}"
            dest_path = os.path.join(os.getcwd(), exe)
            response = requests.get(url, stream=True, timeout=15)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            success_files.append(exe)
        with open(LOCAL_VERSION_FILE, "w") as f:
            f.write(version)
        return success_files
    except Exception as e:
        print(f"Update failed: {e}")
        return []

# === SMTP ===
def save_smtp_credentials_file(from_email, password, to_email, cc1, cc2, smtp_server, smtp_port):
    try:
        with open(SMTP_CREDENTIALS_FILE, "w") as f:
            f.write(f"from_email={from_email}\n")
            f.write(f"password={password}\n")
            f.write(f"to_email={to_email}\n")
            f.write(f"cc1={cc1}\n")
            f.write(f"cc2={cc2}\n")
            f.write(f"smtp_server={smtp_server}\n")
            f.write(f"smtp_port={smtp_port}\n")
        app_logger.info("SMTP credentials saved to file.")
    except IOError as e:
        app_logger.error(f"Error writing SMTP credentials to file: {e}")
        raise

# def get_smtp_credentials_file():
#     if os.path.exists("smtp_credentials.txt"):
#         with open("smtp_credentials.txt", "r") as f:
#             lines = f.readlines()
#             return {line.split("=")[0]: line.split("=")[1].strip() for line in lines}
#     return {}
def get_smtp_credentials_file():
    """Reads SMTP credentials from a plain text file."""
    config = {}
    if os.path.exists(SMTP_CREDENTIALS_FILE):
        try:
            with open(SMTP_CREDENTIALS_FILE, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if "=" in line:
                        key, value = line.split("=", 1) # Split only on the first '='
                        config[key.strip()] = value.strip()
            app_logger.info("SMTP credentials loaded from file.")
        except IOError as e:
            app_logger.error(f"Error reading SMTP credentials from file: {e}")
    else:
        app_logger.warning("smtp_credentials.txt not found.")
    return config

def send_test_email(data):
    from_email = data.get('email')
    password = data.get('password')
    to_email = data.get('recipient_email')
    cc1 = data.get('cc1', '')
    cc2 = data.get('cc2', '')
    smtp_server = data.get('smtp_server')
    smtp_port = data.get('smtp_port')

    if not all([from_email, password, to_email, smtp_server, smtp_port]):
        return False, "Missing essential email configuration for sending test email."

    cc_list = [email for email in [cc1, cc2] if email]

    save_smtp_credentials_file(from_email, password, to_email, cc1, cc2, smtp_server, smtp_port)

    success, message = send_email_with_zip(
        from_email, password, to_email,
        subject="Test Email From Cubi-View",
        body=f"SMTP test from {from_email} using {smtp_server}:{smtp_port}\nCC: {cc_list}",
        attachment_path=None,
        cc_list=cc_list,
        smtp_server_add=smtp_server,
        smtp_port_add=smtp_port
    )
    return success, message

import logging

# Configure logging for the API
# This will log to stderr by default, which Electron can capture
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger('api_logger')
# === WEBSITE WHITELIST / BLOCKLIST ===
def load_sites(file_path):
    try:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump([], f)
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        app_logger.error(f"File not found: {file_path}")
        raise IOError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        app_logger.error(f"Error decoding JSON from {file_path}. File might be corrupted.")
        # Optionally, you could try to back up the corrupted file and start with an empty list
        raise ValueError(f"Invalid JSON in file: {file_path}")
    except IOError as e:
        app_logger.error(f"Permission error or other I/O issue when loading {file_path}: {e}")
        raise IOError(f"Permission denied or I/O error for {file_path}")

def save_sites(file_path, sites):
    try:
        with open(file_path, "w") as f:
            json.dump(sites, f, indent=4)
    except IOError as e:
        app_logger.error(f"Permission error or other I/O issue when saving to {file_path}: {e}")
        raise IOError(f"Permission denied or I/O error for {file_path}")

def add_site(file_path, site):
    try:
        sites = load_sites(file_path)
        if site not in sites:
            sites.append(site)
            save_sites(file_path, sites)
        return sites
    except (IOError, ValueError) as e:
        raise e # Re-raise exceptions from helper functions

def remove_site(file_path, site):
    try:
        sites = load_sites(file_path)
        initial_len = len(sites)
        sites = [s for s in sites if s != site]
        if len(sites) < initial_len: # Check if a site was actually removed
            save_sites(file_path, sites)
        return sites
    except (IOError, ValueError) as e:
        raise e # Re-raise exceptions from helper functions
        
# === INSTALLER WHITELIST ===
def load_whitelisted_installers():
    if os.path.exists(WHITELIST_JSON):
        with open(WHITELIST_JSON, "r") as f:
            data = json.load(f)
            return data.get("WHITELISTED_PROCESSES", [])
    return []

def add_whitelisted_installer(name):
    installers = load_whitelisted_installers()
    if name not in installers:
        installers.append(name)
        with open(WHITELIST_JSON, "w") as f:
            json.dump({"WHITELISTED_PROCESSES": installers}, f, indent=4)
    return installers

def remove_whitelisted_installer(name):
    installers = load_whitelisted_installers()
    installers = [i for i in installers if i != name]
    with open(WHITELIST_JSON, "w") as f:
        json.dump({"WHITELISTED_PROCESSES": installers}, f, indent=4)
    return installers

# === USER INFO ===
def load_user_info():
    if os.path.exists(USER_ID_PATH):
        with open(USER_ID_PATH, "r") as f:
            data = json.load(f)
            return data.get("user", {})
    return {}

def get_system_info():
    print("Gathering system information...")
    print("System ID:", get_system_id())
    return {
        "system_id": get_system_id(),
        "activation_key": load_activation_key(),
        "local_version": get_local_version()
    }

# === MAIN ===
if __name__ == "__main__":
    print("This module provides backend functions; use via API.")
    print(get_system_info())
    print(load_sites(WHITELIST_FILE))
    print(load_sites(BLOCKLIST_FILE))
    