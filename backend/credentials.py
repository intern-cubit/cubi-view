"""
File: credentials.py

Description:
------------
Stores hardcoded admin credentials used for authentication in the Cubi-View application.
Includes the admin username and the SHA-256 hash of the admin password.

Functions Defined:
------------------
(None)

Usage in Other Files:
---------------------
ADMIN_USERNAME, ADMIN_PASSWORD_HASH → Used in: GUI_V2.py

Functions Imported from Other User-defined Modules:
---------------------------------------------------
(None)
"""

import os

# System Paths

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Writable Application Data Directory (for all users) ---
# C:\ProgramData is the standard location for application data shared by all users.
# It's typically writable by standard users.
# It's good practice to create a subdirectory specific to your application.
APP_DATA_COMMON_DIR = "C:\\ProgramData\\CubiView" # Already defined as LOG_DIR, let's reuse it or make it clearer

# Ensure the directory exists when your application starts
# You'll need to call os.makedirs(APP_DATA_COMMON_DIR, exist_ok=True)
# from your main application startup code, as this file just defines paths.

ACTIVATION_PATH = os.path.join(APP_DATA_COMMON_DIR, "activation.json")
USER_ID_PATH = os.path.join(APP_DATA_COMMON_DIR, "user_ID.json")
LOCAL_VERSION_FILE = os.path.join(BASE_DIR, "version.txt") # This would be where your app updates its local version

# Configuration and list files - these absolutely should be in a writable location
CONFIG_PATH = os.path.join(APP_DATA_COMMON_DIR, "monitoring_config.json")
WHITELIST_FILE = os.path.join(APP_DATA_COMMON_DIR, "whitelist_sites.json")
BLOCKLIST_FILE = os.path.join(APP_DATA_COMMON_DIR, "blocklist_sites.json")
WHITELIST_JSON = os.path.join(APP_DATA_COMMON_DIR,"whitelist_installs.json")
BACKUP_FILE_PATH = os.path.join(APP_DATA_COMMON_DIR,"monitor_config_backup.json")
SMTP_CREDENTIALS_FILE = os.path.join(APP_DATA_COMMON_DIR, "smtp_credentials.txt")

# Read-only assets that are deployed with the application (e.g., images)
# These can stay relative to BASE_DIR if they are truly static and not written to.
LOGO_IMAGE = os.path.join(BASE_DIR, "Cubiview-Cubicle.png")

# External URLs (no change needed)
VERSION_URL = "https://github.com/Tanya-M-Vattathil/CuBIT_employee_final/main/version.txt"
RELEASES_URL = "https://github.com/Tanya-M-Vattathil/CuBIT_employee_final/main/download/"

# Log and Report Directories (already correct for being writable)
LOG_DIR = APP_DATA_COMMON_DIR # Reusing the new variable
REPORT_DIR = os.path.join(LOG_DIR,"Reports")

BLOCKED_EXE = [
    # Generic terms
    "setup", "setup.exe", "setup.msi",
    "install", "install.exe", "install.msi",
    "installer", "installer.exe", "installer.msi",
    "installdata", "installdata.exe", "installdata.msi",
    "installexe", "installexe.exe", "installexe.msi",
    "updateinstaller", "updateinstaller.exe", "updateinstaller.msi",
    "appinstaller", "appinstaller.exe", "appinstaller.msi",

    # Uninstallation terms
    "uninstall", "uninstall.exe", "uninstall.msi",
    "unins", "unins.exe", "unins.msi",
    "uninstaller", "uninstaller.exe", "uninstaller.msi",
    "remover", "remover.exe", "remover.msi",
    "removal", "removal.exe", "removal.msi",
    "cleanup", "cleanup.exe", "cleanup.msi",

    # System-level installers -  can be allowed since these are required for system updates
    #"msiexec", "msiexec.exe",
    #"dism", "dism.exe",
    #"wuauclt", "wuauclt.exe",
    #"trustedinstaller", "trustedinstaller.exe",

    # Popular frameworks
    "nsi", "nsi.exe",
    "nsis", "nsis.exe",
    "installshield", "installshield.exe",
    "wiseinstaller", "wiseinstaller.exe",
    "advancedinstaller", "advancedinstaller.exe",
    "inno", "inno.exe",
    "squirrel", "squirrel.exe",
    "choco", "choco.exe",
    "winget", "winget.exe",
    "pip", "pip.exe", #python

    # Web installers
    "websetup", "websetup.exe", "websetup.msi",
    "onlineinstaller", "onlineinstaller.exe", "onlineinstaller.msi",
    "webinstaller", "webinstaller.exe", "webinstaller.msi",
    "downloadinstaller", "downloadinstaller.exe", "downloadinstaller.msi",
]


