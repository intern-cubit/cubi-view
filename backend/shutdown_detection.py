# monitor.py
import datetime
import schedule
import time
import win32api
import win32con
import win32event
from write_report import zip_folder, load_smtp_credentials, send_email_with_zip
from credentials import REPORT_DIR, CONFIG_PATH
import json
from datetime import datetime
import os

from page1_func_part1 import (generate_activity_report, generate_mouse_movement_report, 
                              generate_mouse_click_report, generate_screen_lock_report, generate_location_report)
# Import globals from main tracking module
from page1_func_part2 import ( generate_application_tracking_report,generate_browser_tracking_report,
                       generate_clipboard_report, generate_keylogger_report,
                       generate_keystroke_counter_report,generate_screenshot_capture_report)
from page2_func_part1 import (generate_website_whitelist_report)
from html_report import main_html_report

# config_path = 'monitoring_config.json'

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def generate_enabled_reports():
    config = load_config()

# Call standalone report generators conditionally
    
    if config.get("Capture Screenshots", False):
        generate_screenshot_capture_report()
        print("Screenshots report generated.")
    
    if config.get("Keylogger", False):
        generate_keylogger_report()
        print("Keylogger report generated.")

    if config.get("Application Usage Tracking", False):
        generate_application_tracking_report()
        print("App Tracking report generated.")

    if config.get("Browser History Logging", False):
        generate_browser_tracking_report()
        print("Browser History report generated.")    
    
    if config.get("Keystroke / Word Count", False):
        generate_keystroke_counter_report()
        print("Keystroke counter report generated.")

    if config.get("Active/Idle Time Detection", False):
        generate_activity_report()
        print("Activity report generated.")

    if config.get("Mouse Movement Tracking", False):
        generate_mouse_movement_report()
        print("Mouse movement report generated.")

    if config.get("Mouse Click Count", False):
        generate_mouse_click_report()
        print("Mouse click report generated.")

    if config.get("Detect Login / Logout + Screen Lock / Unlock", False):
        generate_screen_lock_report()
        print("Screen lock report generated.")

    if config.get("Laptop Geolocation (IP/GPS Based)", False):
        generate_location_report()
        print("Location report generated.")

    if config.get("Clipboard Monitoring", False):
        generate_clipboard_report()
        print("Clipboard report generated.")

    if config.get("Website Whitelisting", False):
        generate_website_whitelist_report()
        print("Website whitelist report generated.")



def task_to_run():
    print(f"[{datetime.now()}] >>> Running scheduled/shutdown task.")
    try:
        from_email, password, to_email, cc1, cc2, smtp_server, smtp_port = load_smtp_credentials()

        # Ensure required fields are present
        if not from_email or not password or not to_email:
            print("Missing credentials (From, To and from gmail password)")
            return

        generate_enabled_reports()
        # generate_combined_pdf_report(REPORT_DIR, "Report.pdf")
        main_html_report()


        # Prepare CC list
        cc_list = [email for email in [cc1, cc2] if email]

        # Create ZIP and send
        zip_path = zip_folder()
        send_email_with_zip(
            from_addr=from_email,
            password=password,
            to_addr=to_email,
            subject="Daily Report From Cubi-View",
            body="Dear Team,\nPlease find the attached ZIP file containing today's report.\n\nWarm Regards,\nTeam CuBIT.",
            attachment_path=zip_path,
            cc_list=cc_list,
            smtp_server_add=smtp_server, 
            smtp_port_add = smtp_port
        )
        print("[+] Mail sent successfully")
    except Exception as e:
        print(f"[!] Error during zip creation / Mail not sent")



# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.colors import HexColor, green, red, blue
# from datetime import datetime
# import os
# import json

# def draw_header(c, width, height, date_time_str):
#     # Background
#     c.setFillColor(HexColor("#f6e2ff"))
#     c.rect(0, 0, width, height, fill=1)

#     # Border
#     c.setStrokeColor(HexColor("#53007a"))
#     c.setLineWidth(2)
#     c.rect(20, 20, width - 40, height - 40, stroke=1, fill=0)  # inset border

#     # Centered Title
#     title = "Cubi-View Daily Report"
#     subtitle = "Employee Computer Monitoring and Controlling Application"
#     timestamp = f"Report generated on - {date_time_str}"

#     c.setFillColor(HexColor("#53007a"))

#     c.setFont("Helvetica-Bold", 16)
#     title_width = c.stringWidth(title, "Helvetica-Bold", 16)
#     c.drawString((width - title_width) / 2, height - 40, title)

#     c.setFont("Helvetica", 12)
#     subtitle_width = c.stringWidth(subtitle, "Helvetica", 12)
#     c.drawString((width - subtitle_width) / 2, height - 60, subtitle)

#     c.setFont("Helvetica", 10)
#     timestamp_width = c.stringWidth(timestamp, "Helvetica", 10)
#     c.drawString((width - timestamp_width) / 2, height - 80, timestamp)


def handle_shutdown_event():
    print("[!] Waiting for system shutdown or logoff signal...")
    h = win32event.CreateEvent(None, 0, 0, None)
    while True:
        rc = win32event.MsgWaitForMultipleObjects((h,), 0, win32event.INFINITE, win32con.QS_ALLEVENTS)
        if rc == win32event.WAIT_OBJECT_0:
            break
        while win32api.PumpWaitingMessages():
            msg = win32api.GetMessage(None, 0, 0)
            if msg[1][1] == win32con.WM_QUERYENDSESSION:
                task_to_run()
                return


def run_schedule():
    def daily_wrapper():
        if datetime.now().weekday() != 6:  # Skip Sundays
            print("[✓] Running daily task at 23:59")
            task_to_run()

    def hourly_wrapper():
        print(f"[✓] Hourly report generated at {datetime.now().strftime('%H:%M')}")
        generate_enabled_reports()

    # Schedule daily task
    schedule.every().day.at("23:59").do(daily_wrapper)

    # Schedule hourly task (runs at start of each hour)
    schedule.every().hour.at(":00").do(hourly_wrapper)

    while True:
        schedule.run_pending()
        time.sleep(30)  # check every 30 seconds
