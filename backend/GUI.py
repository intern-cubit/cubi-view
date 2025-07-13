"""
File: GUI.py

Description:
------------
This script defines the main GUI for the Cubi-View employee monitoring software using ttkbootstrap.
It includes an admin login screen and multiple feature pages, such as employee tracking toggles, 
device restriction settings, website whitelisting, installation/uninstallation whitelist, SMTP email configuration, 
employee report viewing, and informational pages like About Us and Privacy Policy.

Functions Defined:
------------------
load_config():
    Loads configuration settings from the 'monitoring_config.json' file.

save_config(config):
    Saves the provided configuration dictionary to 'monitoring_config.json'.

toggle_feature(feature, var):
    Updates the configuration file based on toggle button states for each feature.

save_smtp_credentials(...):
    Stores SMTP email credentials and related settings to a local text file.

send_email_callback(...):
    Validates SMTP fields, saves credentials, and sends a test email using the provided inputs.

main_gui():
    Initializes and runs the main GUI window with the following sub-functions:
    
    - authenticate_admin():
        Verifies admin username and password using a hashed comparison.
    
    - on_show_track_employee():
        Switches view to the employee tracking page and highlights the sidebar button.
    
    - on_show_limit_device():
        Switches view to the device limitation settings page.

    - on_whitelist_websites():
        Switches view to the website whitelisting interface.

    - on_show_install_whitelist():
        Switches view to the installation/uninstallation whitelist interface.

    - on_show_employee_reports():
        Switches view to the employee daily report page.

    - on_smtp():
        Switches view to the SMTP email configuration page.

    - on_about_us():
        Displays company information and contact details.

    - on_privacy_policy():
        Displays the privacy policy page.

    - add_website(), remove_selected():
        Manage the website whitelist entries.

    - add_installer(), remove_selected_installer():
        Manage installer/uninstaller whitelist entries.

Functions Imported from Other User-defined Modules:
---------------------------------------------------
1. ADMIN_USERNAME, ADMIN_PASSWORD_HASH from credentials
2. send_email_with_zip, load_smtp_credentials from write_report
3. WHITELIST_JSON from monitor_installs
4. load_whitelist_sites, save_whitelist_sites from page2_func_part1
"""

import ttkbootstrap as tb
from ttkbootstrap import constants as C
import tkinter as tk  # for tkraise()
from tkinter import ttk
from tkinter import messagebox

import subprocess
import psutil

import json
import requests
import shutil
import tempfile
import os

from tkinterweb import HtmlFrame
from html_report import main_html_report, output_html  
import webbrowser


from credentials import (VERSION_URL, RELEASES_URL, LOGO_IMAGE, ACTIVATION_PATH, 
                         WHITELIST_FILE, BLOCKLIST_FILE, WHITELIST_JSON,
                         LOCAL_VERSION_FILE, CONFIG_PATH, USER_ID_PATH)
from write_report import send_email_with_zip, load_smtp_credentials

# from page2_func_part1 import load_whitelist_sites, save_whitelist_sites
import json
import os
from shutdown_detection import task_to_run 

# ACTIVATION_PATH = "C:\\Users\\ADMIN\\Desktop\\CuBIT_EmployeeTrackingSoftware\\Activation.json"
# LOCAL_VERSION_FILE = "C:\\Users\\ADMIN\\Desktop\\CuBIT_EmployeeTrackingSoftware\\version.txt"
# CONFIG_PATH = "monitoring_config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def toggle_feature(feature, var):
    config = load_config()
    config[feature] = bool(var.get())
    save_config(config)

def save_smtp_credentials(from_email, password, to_email, cc1, cc2,smtp_server, smtp_port, filepath="smtp_credentials.txt"):
    with open(filepath, "w") as f:
        f.write(f"from_email={from_email}\n")
        f.write(f"password={password}\n")
        f.write(f"to_email={to_email}\n")
        f.write(f"cc1={cc1}\n")
        f.write(f"cc2={cc2}\n")
        f.write(f"smtp_server={smtp_server}\n"),
        f.write(f"smtp_port={smtp_port}\n")


# Send Button
def send_email_callback(from_email_var,from_email_pswd_var,to_email_var_1,
                        to_email_var_2,to_email_var_3,smtp_server_var,smtp_port_var):
    from_email = from_email_var.get().strip()
    password = from_email_pswd_var.get().strip()
    to_email = to_email_var_1.get().strip()
    cc1 = to_email_var_2.get().strip()
    cc2 =to_email_var_3.get().strip()
    smtp_server = smtp_server_var.get(). strip()
    smtp_port = smtp_port_var.get(). strip()

    # Filter out empty CCs
    cc_list = [email for email in [cc1, cc2] if email]
    
    # Check required fields
    if not from_email or not password or not to_email or not smtp_server or not smtp_port:
        messagebox.showwarning("Missing Information", "Please fill in From Email, SMTP Server, SMTP Port, " \
        "Password, and To Email address.")
        return

    save_smtp_credentials(from_email, password, to_email, cc1, cc2, smtp_server, smtp_port)

    send_email_with_zip(
        from_email,
        password,
        to_email,
        subject="Test Email From Cubi-View",
        body="Dear Team," \
        "\nThis is just a test email sent from Cubi-View. " \
        "The SMTP details entered are as follows:\n" \
        f"From Address: {from_email}\n" 
        f"SMTP Server: {smtp_server}:{smtp_port}\n"\
        f"CCs: {cc_list}\n\n"\
        "\nWarm Regards,\nTeam CuBIT.",
        attachment_path=None,
        cc_list=cc_list,  # Only non-empty CCs will be sent
        smtp_server_add = smtp_server,
        smtp_port_add = smtp_port
    )



# Import your helper to get system ID
from get_systemID import get_system_id

class WelcomeContentFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.system_id = get_system_id()
        self.activation_key = self.load_activation_key()
        self.local_version = self.get_local_version()
        self.user_data = self.load_user_info()
        self.init_ui()
        self.update_monitoring_status()

    def load_user_info(self):
        try:
            with open(USER_ID_PATH, "r") as f:
                data = json.load(f)
                return data.get("user", {})
        except:
            return {}
        
    def is_monitoring_running(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in ('activator.exe'):
                return True
        return False

    def update_monitoring_status(self):
        running = self.is_monitoring_running()

        if running:
            self.start_btn.config(style="ActiveStart.TButton")
        else:
            self.start_btn.config(style="Start.TButton")

        # call again every second
        self.after(1000, self.update_monitoring_status)

    def init_ui(self):
        user_name = self.user_data.get("fullName", "")
        welcome_text = f"Welcome, {user_name} 👋" if user_name else "Welcome to CubiView"

        title = ttk.Label(self, text=welcome_text, font=("Segoe UI", 16, "bold"))
        title.pack(pady=(20, 10))

        desc = ("Hello! \n Cubi-View is an employee monitoring and endpoint control software.\n"
                "It tracks user activity, application usage, browser history,\n"
                "clipboard, keystrokes, screen locks, and enforces restrictions\n"
                "on USB, downloads, and websites. All data is reported daily.")
        label = ttk.Label(self, text=desc, wraplength=500, justify="left")
        label.pack(pady=(10, 40))

        # System Info Section (copyable)
        sysinfo_text = f"System ID: {self.system_id}\nVersion: {self.local_version}"
        sysinfo_box = tk.Text(self, height=3, width=60, wrap="word", font=("Segoe UI", 9))
        sysinfo_box.insert("1.0", sysinfo_text)
        sysinfo_box.config(state="disabled", background="white", relief="flat")
        sysinfo_box.pack(pady=(0, 20))


        # Activation key section
        activation_frame = ttk.Frame(self)
        activation_frame.pack(pady=(0, 20))

        ttk.Label(activation_frame, text="Activation Key:").pack(side="left", padx=(0, 5))
        self.activation_entry = ttk.Entry(activation_frame, width=30)
        self.activation_entry.pack(side="left", padx=(0, 5))
        self.activation_entry.insert(0, self.activation_key or "")
        save_btn = ttk.Button(activation_frame, text="Save Key", command=self.save_activation_key)
        save_btn.pack(side="left")

        # Styles
        style = ttk.Style()

        style.configure("Start.TButton", foreground="#0078D7", background="white")
        style.map("Start.TButton",
            background=[('active', 'white')],
            foreground=[('active', '#0078D7')]
        )

        style.configure("ActiveStart.TButton", foreground="white", background="#0078D7")
        style.map("ActiveStart.TButton",
            background=[('active', '#0078D7')],
            foreground=[('active', 'white')]
        )

        style.configure("Stop.TButton", foreground="#0078D7", background="white")
        style.map("Stop.TButton",
            background=[('active', 'white')],
            foreground=[('active', '#0078D7')]
        )

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(anchor='center', padx=20)

        self.start_btn = ttk.Button(button_frame, text="Start Monitoring", style="Start.TButton", command=self.start_monitoring)
        self.stop_btn = ttk.Button(button_frame, text="Stop Monitoring", style="Stop.TButton", command=self.stop_monitoring)
        update_btn = ttk.Button(self, text="Check for Updates", command=self.check_and_prompt_update)

        self.start_btn.pack(side="left", padx=(0, 10))
        self.stop_btn.pack(side="left")
        update_btn.pack(pady=10)

    def load_activation_key(self):
        if os.path.exists(ACTIVATION_PATH):
            try:
                with open(ACTIVATION_PATH, 'r') as f:
                    data = json.load(f)
                    return data.get("activationKey", "")
            except:
                return ""
        return ""

    def save_activation_key(self):
        key = self.activation_entry.get().strip()
        if not key:
            messagebox.showwarning("Input Error", "Please enter an activation key.")
            return

        data = {
            "activationKey": key,
            "systemId": self.system_id
        }
        try:
            with open(ACTIVATION_PATH, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", "Activation key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save activation key.\n{e}")

    def get_local_version(self):
        if os.path.exists(LOCAL_VERSION_FILE):
            try:
                with open(LOCAL_VERSION_FILE, "r") as f:
                    return f.read().strip()
            except:
                return "Error reading version"
        return "Unknown"

    def get_remote_version(self):
        try:
            response = requests.get(VERSION_URL, timeout=5)
            return response.text.strip()
        except:
            return None

    def start_monitoring(self):
        try:
            # Use activator.py directly for testing; replace with activator.exe in production
            subprocess.Popen(["activator.py"], shell=False)
        except Exception as e:
            messagebox.showerror("Error", f"Could not start monitoring.\n{e}")

    def stop_monitoring(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() in ('activator.exe'):
                proc.terminate()
                messagebox.showinfo("Stopped", "[✓] Monitoring stopped.")
                return
        messagebox.showinfo("Info", "Monitoring was not running.")

    def perform_full_update(self, version):
        files_to_update = ["GUI.exe", "activator.exe"]
        success_files = []

        try:
            for exe in files_to_update:
                url = f"{RELEASES_URL}{exe}"
                dest_path = os.path.join(os.getcwd(), exe)
                old_backup = os.path.join(tempfile.gettempdir(), f"old_{exe}")

                if os.path.exists(dest_path):
                    shutil.move(dest_path, old_backup)

                response = requests.get(url, stream=True, timeout=15)
                with open(dest_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                success_files.append(exe)

            with open(LOCAL_VERSION_FILE, "w") as f:
                f.write(version)

            messagebox.showinfo("Update Successful", f"Updated files: {', '.join(success_files)}")
        except Exception as e:
            messagebox.showerror("Update Failed", f"Error: {e}")

    def check_and_prompt_update(self):
        try:
            local_version = self.get_local_version()
            remote_version = self.get_remote_version()

            if not remote_version:
                messagebox.showwarning("Update Error", "Could not fetch the latest version.")
                return

            if remote_version > local_version:
                response = messagebox.askyesnocancel(
                    "Update Available",
                    f"A new version is available.\n\nLocal: v{local_version}\nRemote: v{remote_version}\n\nDo you want to update now?"
                )

                if response is True:
                    self.perform_full_update(remote_version)
                elif response is False:
                    messagebox.showinfo("Update Skipped", "You can update later from the Welcome page.")
                else:
                    print("User cancelled the update prompt.")
            else:
                response = messagebox.askyesno(
                    "Up to Date",
                    f"You are already on the latest version (v{local_version}).\n\nDo you want to re-download it anyway?"
                )
                if response:
                    self.perform_full_update(remote_version)
        except Exception as e:
            messagebox.showerror("Update Failed", str(e))

# ====== MAIN APPLICATION SETUP ======
#app = tb.Window(themename="cyborg")
def main_gui():
    app = tb.Window(themename="cosmo")
    # app = tb.Window(themename="cyborg")
    app.title("Cubi-View")
    app.geometry("1000x600")

    app.iconphoto(False, tk.PhotoImage(file=LOGO_IMAGE))
    # app.iconphoto(False, tk.PhotoImage(file=r"C:\\Users\\ADMIN\\Desktop\\CuBIT_EmployeeTrackingSoftware\\Cubiview-Cubicle.png"))
    app.resizable(False, False)

    # ========================= LOGIN PAGE ================================
    def authenticate_admin():
        entered_username = username_var.get()
        entered_password = password_var.get()

        try:
            res = requests.post("https://cubiview.onrender.com/api/auth/login", json={
                "identifier": entered_username,
                "password": entered_password
            }, timeout=10)

            res_data = res.json()
            print("Server response:", res_data)  # Add this line

            if res.status_code == 200 and "token" in res_data and "user" in res_data:
                user = res_data["user"]
                with open(USER_ID_PATH, "w") as f:
                    json.dump({
                        "user": user
                    }, f, indent=4)
                login_frame.pack_forget()
                sidebar.pack(side=C.LEFT, fill=C.Y)
                container.pack(side=C.LEFT, fill=C.BOTH, expand=True)
                on_show_welcome()
            else:
                messagebox.showerror("CubiView", res_data.get("message", "Login Failed, Invalid credentials."))
        except Exception as e:
            messagebox.showerror("CubiView", f"Connection Error. Could not connect to server:\n{e}")

    def ask_forgot_credentials():
        dialog = tk.Toplevel()
        dialog.title("CubiView - Forgot Password")
        dialog.geometry("400x200")
        dialog.grab_set()  # Make modal so user must interact

        tk.Label(dialog, text="Enter your registered email:").pack(pady=(15, 5))
        email_entry = tk.Entry(dialog, width=40)
        email_entry.pack()

        def submit():
            username = username_entry.get()
            email = email_entry.get()
            if not email:
                messagebox.showerror("CubiView", "Please fill in email field.")
            else:
                dialog.destroy()
                send_reset_request(email)

        tk.Button(dialog, text="Submit", command=submit).pack(pady=20)


    def send_reset_request(email):
        try:
            res = requests.post("https://cubiview.onrender.com/api/auth/forgot-password", json={
                "email": email
            }, timeout=10)

            res_data = res.json()
            if res.status_code == 200 and res_data.get("success"):
                messagebox.showinfo("CubiView", "A reset link has been sent to your email.")
            else:
                messagebox.showerror("CubiView", res_data.get("message", "Failed to send reset email."))
        except Exception as e:
            messagebox.showerror("CubiView", f"Could not connect to server:\n{e}")


    
    # Frame setup
    login_frame = tb.Frame(app, padding=40)
    login_frame.pack(fill="both", expand=True)

    # 🧩 Configure 3 columns to center things in column=1
    for i in range(3):
        login_frame.grid_columnconfigure(i, weight=1)

    # Logo (centered across all 3 columns)
    logo_img = tk.PhotoImage(file=LOGO_IMAGE).subsample(3, 3)
    # logo_img = tk.PhotoImage(file=r"C:\\Users\\ADMIN\\Desktop\\CuBIT_EmployeeTrackingSoftware\\Cubiview-Cubicle.png").subsample(3, 3)
    logo_label = tk.Label(login_frame, image=logo_img)
    logo_label.image = logo_img
    logo_label.grid(row=0, column=0, columnspan=3, pady=(10, 30))

    # Title (also centered)
    tb.Label(login_frame, text="Admin Login", font=("Poppins", 18, "bold")).grid(row=1, column=0, columnspan=3, pady=(0, 20))

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    # Username row
    tb.Label(login_frame, text="Username", font=("Segoe UI", 10)).grid(
        row=2, column=1, sticky="w", padx=(100, 2), pady=5
    )
    username_entry = tb.Entry(login_frame, textvariable=username_var, width=30)
    username_entry.grid(row=2, column=1, columnspan=2, sticky="n", padx=(5, 80), pady=5)

    # Password row
    tb.Label(login_frame, text="Password", font=("Segoe UI", 10)).grid(
        row=3, column=1, sticky="w", padx=(100, 2), pady=5
    )
    password_entry = tb.Entry(login_frame, textvariable=password_var, show="*", width=30)
    password_entry.grid(row=3, column=1, columnspan=2, sticky="n", padx=(5, 80), pady=5)


    # Login Button (centered across 3 columns)
    login_btn = tb.Button(login_frame, text="Login", bootstyle="success", width=25, 
                          command=authenticate_admin)
    login_btn.grid(row=4, column=0, columnspan=3, pady=20)

    # Forgot Password Button
    forgot_btn = tb.Button(login_frame, text="Forgot Password?", bootstyle="link", command=ask_forgot_credentials)
    forgot_btn.grid(row=5, column=0, columnspan=3)

    # ====== SIDEBAR ======
    sidebar = tb.Frame(app, padding=10, bootstyle="light")
    #sidebar.pack(side=C.LEFT, fill=C.Y)

    # 1. Dictionary to keep track of buttons
    sidebar_buttons = {}

    def highlight_sidebar_button(name):
        for key, btn in sidebar_buttons.items():
            btn.configure(bootstyle="primary-outline")
        sidebar_buttons[name].configure(bootstyle="primary")  # Highlight current

    # 2. Wrap original command to also highlight
    def on_show_welcome():
        welcome_frame.tkraise()
        highlight_sidebar_button("welcome")

    def on_show_track_employee():
        track_employee_frame.tkraise() #Switch page on button click
        highlight_sidebar_button("track")

    def on_show_limit_device():
        limit_device_frame.tkraise()
        highlight_sidebar_button("limit")

    def on_whitelist_websites():
        whitelist_web_frame.tkraise()
        highlight_sidebar_button("website")

    def on_show_install_whitelist():
        install_whitelist_frame.tkraise()
        highlight_sidebar_button("install_whitelist")

    def on_show_employee_reports():
        employee_report_frame.tkraise()
        highlight_sidebar_button("report")

    def on_smtp():
        smtp_frame.tkraise()
        highlight_sidebar_button("smtp")

    def on_about_us():
        about_us_frame.tkraise()
        highlight_sidebar_button("about")

    def on_privacy_policy():
        privacy_policy_frame.tkraise()
        highlight_sidebar_button("privacy")

    # 3. Create buttons and register them
    sidebar_buttons["welcome"] = tb.Button(sidebar, text="Welcome", bootstyle="primary-outline", command=on_show_welcome)
    sidebar_buttons["welcome"].pack(fill=C.X, pady=5)


    sidebar_buttons["track"] = tb.Button(sidebar, text="Track Employee", bootstyle="primary-outline", command=on_show_track_employee)
    sidebar_buttons["track"].pack(fill=C.X, pady=5)

    sidebar_buttons["limit"] = tb.Button(sidebar, text="Limit Device Functionality", bootstyle="primary-outline", command=on_show_limit_device)
    sidebar_buttons["limit"].pack(fill=C.X, pady=5)

    sidebar_buttons["website"] = tb.Button(sidebar, text="Whitelist Websites", bootstyle="primary-outline", command=on_whitelist_websites)
    sidebar_buttons["website"].pack(fill=C.X, pady=5)

    sidebar_buttons["install_whitelist"] = tb.Button(sidebar, text="Whitelist Installs/Uninstalls", bootstyle="primary-outline", command=on_show_install_whitelist)
    sidebar_buttons["install_whitelist"].pack(fill=C.X, pady=5)

    sidebar_buttons["report"] = tb.Button(sidebar, text="View Employee Report", bootstyle="primary-outline", command=on_show_employee_reports)
    sidebar_buttons["report"].pack(fill=C.X, pady=5)

    sidebar_buttons["smtp"] = tb.Button(sidebar, text="SMTP", bootstyle="primary-outline", command=on_smtp)
    sidebar_buttons["smtp"].pack(fill=C.X, pady=5)

    sidebar_buttons["about"] = tb.Button(sidebar, text="About Us", bootstyle="primary-outline", command=on_about_us)
    sidebar_buttons["about"].pack(fill=C.X, pady=5)

    sidebar_buttons["privacy"] = tb.Button(sidebar, text="Privacy Policy", bootstyle="primary-outline", command=on_privacy_policy)
    sidebar_buttons["privacy"].pack(fill=C.X, pady=5)


    # ====== CONTENT CONTAINER ======
    # Create a container frame to hold both pages
    container = tb.Frame(app)
    #container.pack(side=C.LEFT, fill=C.BOTH, expand=True)

    # ====== WELCOME PAGE ======= 
    welcome_frame = WelcomeContentFrame(container)
    welcome_frame.grid(row=0, column=0, sticky="nsew")


    # ====== PAGE 1: TRACK EMPLOYEE ======
    track_employee_frame = tb.Frame(container, padding=20)
    track_employee_frame.grid(row=0, column=0, sticky="nsew")
    # Make sure container resizes properly
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    header = tb.Label(
        track_employee_frame,
        text="Customise your Employee Tracker",
        font=("Lobster", 18),
        anchor="w"
    )
    header.pack(fill=C.X, padx=20, pady=(10, 0))

    # ====== FEATURES LIST WITH TOGGLES ======
    features = [
        "Keylogger","Keystroke / Word Count", "Mouse Click Count",  "Mouse Movement Tracking",
        "Active/Idle Time Detection", "Clipboard Monitoring", "Print Job Monitoring",
        "Browser History Logging",  "Application Usage Tracking",
        "Detect Login / Logout + Screen Lock / Unlock", "Capture Screenshots",
        "Capture Audio Clips", "Capture Video Clips", 
        "Installation / Uninstallation Logs",
        "Laptop Geolocation (IP/GPS Based)"
    ]

    # This frame will hold the checkbuttons (you may add a scrollable canvas later if needed)
    features_frame = tb.Frame(track_employee_frame, padding=20)
    features_frame.pack(fill=C.BOTH, expand=True)

    # Save BooleanVars in a dict if you need to reference them later
    feature_vars_p1 = {}
    initial_config = load_config()

    for i, feature in enumerate(features):
        var = tb.BooleanVar(value=initial_config.get(feature, False))
        feature_vars_p1[feature] = var
        # Create a checkbutton with a lambda capturing `feature` and its variable.
        chk = tb.Checkbutton(
            features_frame,
            text=feature,
            variable=var,
            bootstyle="success-round-toggle",
            command=lambda f=feature, v=var: toggle_feature(f, v)
        )
        # Arrange in a grid, two columns.
        chk.grid(row=i // 2, column=i % 2, sticky="w", padx=15, pady=15)

    # ====== PAGE 2: LIMIT DEVICE FUNCTIONALITY ======
    limit_device_frame = tb.Frame(container, padding=20)
    limit_device_frame.grid(row=0, column=0, sticky="nsew")

    # Here you can add your limit device functionality components.
    limit_header = tb.Label(
        limit_device_frame,
        text="Limit Device Functionality Settings",
        font=("Lobster", 18),
        anchor="w"
    )
    limit_header.pack(fill=C.X, padx=20, pady=(10, 0))

    # ====== FEATURES LIST WITH TOGGLES ======
    features_p2 = [
        "VPN Detection & Blocking", "Chrome Extension Restrictions",
        "USB Port Access Control", 
        "Incognito Mode Blocking",
        "Website Whitelisting", "Website Blocking" ,"Screenshot / Snipping Tool Prevention",
        "Copy-Paste Enable / Disable",
        "Download Enable / Disable",
        "Built-in Ad Blocker", "Custom Antivirus & Spam Link Detection",
        "Internet / Screen Time Limits", 
        "Lunch Break Mode"
    ]

    # This frame will hold the checkbuttons (you may add a scrollable canvas later if needed)
    features_frame = tb.Frame(limit_device_frame, padding=20)
    features_frame.pack(fill=C.BOTH, expand=True)

    # Save BooleanVars in a dict if you need to reference them later
    feature_vars_p2 = {}
    initial_config = load_config()

    for i, feature in enumerate(features_p2):
        var = tb.BooleanVar(value=initial_config.get(feature, False))
        feature_vars_p2[feature] = var
        # Create a checkbutton with a lambda capturing `feature` and its variable.
        chk = tb.Checkbutton(
            features_frame,
            text=feature,
            variable=var,
            bootstyle="success-round-toggle",
            command=lambda f=feature, v=var: toggle_feature(f, v)
        )
        # Arrange in a grid, two columns.
        chk.grid(row=i // 2, column=i % 2, sticky="w", padx=15, pady=15)


    # ====== PAGE 3: Website Whitelisting ======
    whitelist_web_frame = tb.Frame(container, padding=20)
    whitelist_web_frame.grid(row=0, column=0, sticky="nsew")

    whitelist_header = tb.Label(
        whitelist_web_frame,
        text="Website Whitelisting",
        font=("Lobster", 18),
        anchor="w"
    )
    whitelist_header.pack(fill=tk.X, padx=20, pady=(10, 0))

    # Entry
    entry_var_web = tk.StringVar()
    entry = tb.Entry(whitelist_web_frame, textvariable=entry_var_web, width=40)
    entry.pack(pady=10)

    # Frame to hold both lists side-by-side
    lists_frame = tb.Frame(whitelist_web_frame)
    lists_frame.pack(fill="both", expand=True, padx=10)

    # === Whitelist Listbox ===
    whitelist_box = tk.Listbox(lists_frame, height=12)
    whitelist_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # === Blocklist Listbox ===
    blocklist_box = tk.Listbox(lists_frame, height=12)
    blocklist_box.pack(side="left", fill="both", expand=True)

    # ====== Button Frame ======
    button_frame = tb.Frame(whitelist_web_frame)
    button_frame.pack(pady=10)

    # ====== Data Handling ======

    def initialize_files():
        """Initialize JSON files if they don't exist."""
        for file_path in [WHITELIST_FILE, BLOCKLIST_FILE]:
            if not os.path.exists(file_path):
                try:
                    with open(file_path, "w") as f:
                        json.dump([], f)
                    print(f"Created {file_path}")
                except Exception as e:
                    messagebox.showerror("CubiView Error", f"Failed to create {file_path}: {e}")

    def load_sites(file_path):
        """Load sites from a JSON file."""
        try:
            if not os.path.exists(file_path):
                initialize_files()
            with open(file_path, "r") as f:
                data = f.read().strip()
                sites = json.loads(data) if data else []
                print(f"Loaded from {file_path}: {sites}")
                return sites
        except json.JSONDecodeError as e:
            print(f"Error: {file_path} is corrupted or not valid JSON: {e}")
            messagebox.showerror("Error", f"Corrupted file {file_path}. Resetting it.")
            save_sites(file_path, [])
            return []
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to load {file_path}: {e}")
            return []

    def save_sites(file_path, sites):
        """Save sites to a JSON file."""
        try:
            with open(file_path, "w") as f:
                json.dump(sites, f, indent=4)
            print(f"Saved to {file_path}: {sites}")
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to save {file_path}: {e}")

    def refresh_lists():
        """Refresh the whitelist and blocklist listboxes."""
        whitelist_box.delete(0, tk.END)
        whitelist = load_sites(WHITELIST_FILE)
        for site in whitelist:
            whitelist_box.insert(tk.END, site)
        print(f"Refreshed whitelist: {whitelist}")

        blocklist_box.delete(0, tk.END)
        blocklist = load_sites(BLOCKLIST_FILE)
        for site in blocklist:
            blocklist_box.insert(tk.END, site)
        print(f"Refreshed blocklist: {blocklist}")

    # ====== Button Actions ======
    def validate_url(site):
        """Basic URL validation."""
        if not site:
            return False, "Please enter a website."
        # Add more validation if needed (e.g., regex for URL format)
        return True, ""

    def add_to_whitelist():
        """Add a site to the whitelist."""
        site = entry_var_web.get().strip().lower()
        valid, error_msg = validate_url(site)
        if not valid:
            messagebox.showwarning("Invalid Input", error_msg)
            return
        print(f"Attempting to add {site} to whitelist")
        wl = load_sites(WHITELIST_FILE)
        if site not in wl:
            wl.append(site)
            save_sites(WHITELIST_FILE, wl)
            refresh_lists()
            entry_var_web.set("")
            print(f"Added {site} to whitelist")
        else:
            messagebox.showinfo("Exists", f"{site} is already whitelisted.")

    def remove_from_whitelist():
        """Remove a site from the whitelist."""
        sel = whitelist_box.curselection()
        if sel:
            wl = load_sites(WHITELIST_FILE)
            site = wl[sel[0]]
            wl.pop(sel[0])
            save_sites(WHITELIST_FILE, wl)
            refresh_lists()
            print(f"Removed {site} from whitelist")
        else:
            messagebox.showwarning("No Selection", "Please select a site to remove.")

    def add_to_blocklist():
        """Add a site to the blocklist."""
        site = entry_var_web.get().strip().lower()
        valid, error_msg = validate_url(site)
        if not valid:
            messagebox.showwarning("Invalid Input", error_msg)
            return
        print(f"Attempting to add {site} to blocklist")
        bl = load_sites(BLOCKLIST_FILE)
        if site not in bl:
            bl.append(site)
            save_sites(BLOCKLIST_FILE, bl)
            refresh_lists()
            entry_var_web.set("")
            print(f"Added {site} to blocklist")
        else:
            messagebox.showinfo("Already Exists", f"{site} is already in the blocklist.")

    def remove_from_blocklist():
        """Remove a site from the blocklist."""
        sel = blocklist_box.curselection()
        if sel:
            bl = load_sites(BLOCKLIST_FILE)
            site = bl[sel[0]]
            bl.pop(sel[0])
            save_sites(BLOCKLIST_FILE, bl)
            refresh_lists()
            print(f"Removed {site} from blocklist")
        else:
            messagebox.showwarning("No Selection", "Please select a site to remove.")

    # ====== Buttons ======
    tb.Button(button_frame, text="Add to Whitelist", bootstyle="success", command=add_to_whitelist).pack(side="left", padx=5)
    tb.Button(button_frame, text="Remove from Whitelist", bootstyle="danger", command=remove_from_whitelist).pack(side="left", padx=5)
    tb.Button(button_frame, text="Add to Blocklist", bootstyle="success", command=add_to_blocklist).pack(side="left", padx=5)
    tb.Button(button_frame, text="Remove from Blocklist", bootstyle="danger", command=remove_from_blocklist).pack(side="left", padx=5)

    # Initialize files and load initial data
    initialize_files()
    refresh_lists()


    # ====== PAGE =============
    install_whitelist_frame = tb.Frame(container, padding=20)
    install_whitelist_frame.grid(row=0, column=0, sticky="nsew")
 
    install_whitelist_header = tb.Label(
        install_whitelist_frame,
        text="Whitelist Install",
        font=("Lobster", 18),
        anchor="w"
    )
    install_whitelist_header.pack(fill=C.X, padx=20, pady=(10, 0))

    def refresh_whitelist_list():
        whitelist_listbox.delete(0, tk.END)
        if os.path.exists(WHITELIST_JSON):
            with open(WHITELIST_JSON, "r") as f:
                data = json.load(f)
                for proc in data.get("WHITELISTED_PROCESSES", []):
                    whitelist_listbox.insert(tk.END, proc)

    def add_installer():
        new_value = entry_var.get().strip().lower()
        if not new_value:
            messagebox.showwarning("Empty Entry", "Please enter a process name.")
            return

        data = {}
        if os.path.exists(WHITELIST_JSON):
            with open(WHITELIST_JSON, "r") as f:
                data = json.load(f)

        data.setdefault("WHITELISTED_PROCESSES", [])
        if new_value in data["WHITELISTED_PROCESSES"]:
            messagebox.showinfo("Exists", f"'{new_value}' is already whitelisted.")
        else:
            data["WHITELISTED_PROCESSES"].append(new_value)
            with open(WHITELIST_JSON, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"'{new_value}' has been added.")
            entry_var.set("")
            refresh_whitelist_list()

    def remove_selected_installer():
        sel = whitelist_listbox.curselection()
        if not sel:
            return
        selected_item = whitelist_listbox.get(sel[0])
        with open(WHITELIST_JSON, "r") as f:
            data = json.load(f)
        data["WHITELISTED_PROCESSES"] = [item for item in data.get("WHITELISTED_PROCESSES", []) if item != selected_item]
        with open(WHITELIST_JSON, "w") as f:
            json.dump(data, f, indent=4)
        refresh_whitelist_list()


    whitelist_listbox = tk.Listbox(install_whitelist_frame, height=8)
    whitelist_listbox.pack(fill="both", expand=True, padx=10, pady=10)
    refresh_whitelist_list()

    entry_var = tk.StringVar()
    entry = tb.Entry(install_whitelist_frame, textvariable=entry_var, width=40)
    entry.pack(pady=(5, 10))

    tb.Button(install_whitelist_frame, text="Add Installer", bootstyle="success", command=add_installer).pack(side="left", padx=5)
    tb.Button(install_whitelist_frame, text="Remove Selected", bootstyle="danger", command=remove_selected_installer).pack(side="right", padx=5)
    refresh_whitelist_list()

    # ====== PAGE 4: EMPLOYEE REPORT FRAME ======
    employee_report_frame = tb.Frame(container, padding=20)
    employee_report_frame.grid(row=0, column=0, sticky="nsew")

    # Header Label
    report_header = tb.Label(
        employee_report_frame,
        text="Daily Work Report of Employee No.1",
        font=("Lobster", 18),
        anchor="w"
    )
    report_header.pack(fill=C.X, padx=20, pady=(10, 0))

    # Generate Report Function
    import time

    def refresh_html_report():
        main_html_report()
        time.sleep(0.1)  # slight delay to ensure file is saved
        if os.path.exists(output_html):
            html_view.load_website("about:blank")
            html_view.load_file(output_html)
        else:
            messagebox.showerror("Error", "Report file not found. Please generate the report first.")




    # Button
    generate_button = tb.Button(
        employee_report_frame,
        text="Generate New Report",
        command=refresh_html_report,
        bootstyle="success-outline"
    )
    generate_button.pack(pady=(5, 10))

    report_link = tb.Label(
        employee_report_frame,
        text="📂 Open Full Report in Browser",
        foreground="blue",
        cursor="hand2",
        font=("Segoe UI", 10, "underline")
    )
    report_link.pack(pady=(10, 5))

    # Link to open the HTML report in default browser
    report_link.bind("<Button-1>", lambda e: webbrowser.open(f"file:///{output_html.replace(os.sep, '/')}"))


    # Embedded HTML Viewer
    html_view = HtmlFrame(employee_report_frame, horizontal_scrollbar="auto")
    html_view.pack(fill="both", expand=True, padx=10, pady=10)

    # Load initially if file exists
    if os.path.exists(output_html):
        html_view.load_file(output_html)

    # ====== PAGE 4: Simple Mail Transfer Protocol ======
    smtp_frame = tb.Frame(container, padding=20)
    smtp_frame.grid(row=0, column=0, sticky="nsew")

    # Here you can add your limit device functionality components.
    SMTP_header = tb.Label(
        smtp_frame,
        text="Simple Mail Transfer Protocol",
        font=("Lobster", 18),
        anchor="w"
    )
    SMTP_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 0))

    from_email_var = tk.StringVar()
    smtp_server_var = tk.StringVar()
    smtp_port_var = tk.StringVar()
    from_email_pswd_var = tk.StringVar()
    to_email_var_1 = tk.StringVar()
    to_email_var_2 = tk.StringVar()
    to_email_var_3 = tk.StringVar()

    # Load saved credentials and populate fields
    from_email, password, to_email, cc1, cc2, smtp_server, smtp_port = load_smtp_credentials()

    from_email_var.set(from_email)
    from_email_pswd_var.set(password)
    to_email_var_1.set(to_email)
    to_email_var_2.set(cc1)
    to_email_var_3.set(cc2)
    smtp_server_var.set(smtp_server)
    smtp_port_var.set(smtp_port)


    # Label and Entry: From Email
    tb.Label(smtp_frame, text="From email address:").grid(row=9, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=from_email_var, width=40).place(x=250, y=70)

    # Label and Entry: Email Password
    tb.Label(smtp_frame, text="SMTP Server:").grid(row=13, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=smtp_server_var, width=40).place(x=250, y=125)

    # Label and Entry: SMTP
    tb.Label(smtp_frame, text="SMTP Port:").grid(row=17, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=smtp_port_var, width=40).place(x=250, y=180)

    # Label and Entry: Email Password
    tb.Label(smtp_frame, text="App password:").grid(row=21, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=from_email_pswd_var,show="*", width=40).place(x=250, y=235)

    # Label and Entry: To Email
    tb.Label(smtp_frame, text="Primary recipient (To):").grid(row=25, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=to_email_var_1, width=40).place(x=250, y=285)

    # CC recipient 1
    tb.Label(smtp_frame, text="CC recipient 1:").grid(row=29, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=to_email_var_2, width=40).place(x=250, y=340)

    # CC recipient 2
    tb.Label(smtp_frame, text="CC recipient 2:").grid(row=34, column=0, sticky="w", padx=(15, 5), pady=(25,5))
    tb.Entry(smtp_frame, textvariable=to_email_var_3, width=40).place(x=250, y=390)

    tb.Button(smtp_frame, text="Save and send Test Email", 
              command=lambda: send_email_callback(from_email_var,from_email_pswd_var,to_email_var_1,
                        to_email_var_2,to_email_var_3,smtp_server_var,smtp_port_var)).grid(row= 45,  pady=(25,5))

    tb.Label(smtp_frame, text="Please Note: Once the \"From\" and \"To\" emails addresses are set, " \
    "the employee's reports \nof each day will be emailed automatically to the \"To\" address").grid(pady=20)

    # ====== PAGE 5: About Us ======
    about_us_frame = tb.Frame(container, padding=20)
    about_us_frame.grid(row=0, column=0, sticky="nsew")

    # ---- Load and show company logo using tk.PhotoImage ----
    # CuBIT_logo_path = "add Cubit logo .png file only"  # Must be a supported .png file

    # try:
    #     logo_photo = tk.PhotoImage(file=CuBIT_logo_path)

    #     logo_label = tb.Label(about_us_frame, image=logo_photo)
    #     logo_label.image = logo_photo  # Prevent garbage collection
    #     logo_label.pack(pady=(10, 10))
    # except Exception as e:
    #     tb.Label(about_us_frame, text="Logo not found", foreground="red").pack(pady=(10, 10))
    #     print("Logo loading error:", e)

    # Here you can add your limit device functionality components.
    limit_header = tb.Label(
        about_us_frame,
        text="About CuBIT Dynamics",
        font=("Lobster", 20),
        foreground="#b79d61",
        anchor="w"
    )
    limit_header.pack(fill=C.X, padx=20, pady=(10, 0))

    # ---- Description Text ----
    about_text = (
        "\nWe are a stealth-mode company building fully customized hardware and software solutions.\n"
        "No templated products, no fluff — just exact quotations, high-quality R&D, and on-time delivery.\n"
        "Every project is case-specific, crafted by a dedicated team including experts from Germany & China.\n"
        "We don’t just advertise — we deliver.\n"
        "Want us to customize a product for you? Or build something entirely new?\n"
        "Connect with us now!\n\n\n"
        " www.cubitdynamics.com | info@cubitdynamics.com | +91 86185 09818"
    )

    tb.Label(
        about_us_frame,
        text=about_text,
        wraplength=600,
        justify="left",
        font=("Segoe UI", 11),
        foreground="#83745c"
    ).pack(padx=20, pady=10)

    # ====== PAGE 6: Privacy Policy ======
    privacy_policy_frame = tb.Frame(container, padding=20)
    privacy_policy_frame.grid(row=0, column=0, sticky="nsew")

    # Here you can add your limit device functionality components.
    limit_header = tb.Label(
        privacy_policy_frame,
        text="Privacy Policy",
        font=("Lobster", 18),
        anchor="w"
    )
    limit_header.pack(fill=C.X, padx=20, pady=(10, 0))

    # Placeholder for additional controls:
    tb.Label(privacy_policy_frame, text="(Privacy Policy will be populated here.)").pack(pady=20)


    app.mainloop()

if __name__ == "__main__":
    main_gui()
