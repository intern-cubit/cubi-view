import os
import re
import json
from datetime import datetime
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
import math
import zipfile
import requests
import logging

# Assuming credentials.py is accessible and contains these paths
# You would need to ensure credentials.py exists and has these defined:
# Example credentials.py:
# REPORT_DIR = 'reports'
# CONFIG_PATH = 'config.json'
try:
    from credentials import REPORT_DIR, CONFIG_PATH
except ImportError:
    print("[ERROR] 'credentials.py' not found or missing REPORT_DIR/CONFIG_PATH. Using defaults.")
    REPORT_DIR = 'reports'
    CONFIG_PATH = 'config.json'
except Exception as e:
    print(f"[ERROR] Error importing from credentials.py: {e}. Using defaults.")
    REPORT_DIR = 'reports'
    CONFIG_PATH = 'config.json'

# Import get_system_id for cloud upload
try:
    from get_systemID import get_system_id
except ImportError:
    print("[ERROR] Failed to import get_system_id. Cloud upload will not work.")
    def get_system_id():
        return "unknown"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
html_report_logger = logging.getLogger('html_report_logger')


# === Global Variables for Report Data ===
# These globals are primarily updated by parse_reports and then used by main_html_report
# to pass specific values to chart generation functions.
active_time = 0
idle_time = 0
total_keystrokes = 0
total_words = 0
total_clicks = 0
application_data = []
browser_data = []

def extract_value(text, keyword):
    """Extracts an integer value following a keyword from a string."""
    match = re.search(rf"{re.escape(keyword)}\D*(\d+)", text)
    return int(match.group(1)) if match else 0

def parse_reports(current_report_dir):
    """Parses activity, keystroke, and click reports to update global totals."""
    global active_time, idle_time, total_keystrokes, total_words, total_clicks

    activity_path = os.path.join(current_report_dir, "activity_report.txt")
    keystroke_path = os.path.join(current_report_dir, "keystroke_report.txt")
    click_path = os.path.join(current_report_dir, "mouse_click_report.txt")

    # Reset totals before parsing to avoid accumulation on multiple calls
    active_time = 0
    idle_time = 0
    total_keystrokes = 0
    total_words = 0
    total_clicks = 0

    if os.path.exists(activity_path):
        try:
            with open(activity_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "Working Time" in line:
                        active_time += extract_value(line, "Working Time")
                    elif "Idle Time" in line:
                        idle_time += extract_value(line, "Idle Time")
        except Exception as e:
            print(f"[ERROR] Could not read activity report {activity_path}: {e}")
    else:
        print(f"[WARNING] Activity report not found: {activity_path}")

    if os.path.exists(keystroke_path):
        try:
            with open(keystroke_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    total_keystrokes += extract_value(line, "Total Keystrokes")
                    total_words += extract_value(line, "Total Words Typed")
        except Exception as e:
            print(f"[ERROR] Could not read keystroke report {keystroke_path}: {e}")
    else:
        print(f"[WARNING] Keystroke report not found: {keystroke_path}")

    if os.path.exists(click_path):
        try:
            with open(click_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    total_clicks += extract_value(line, "Total Clicks")
        except Exception as e:
            print(f"[ERROR] Could not read mouse click report {click_path}: {e}")
    else:
        print(f"[WARNING] Mouse click report not found: {click_path}")

def read_text_file_if_exists(current_report_dir, filename):
    """Reads content of a text file if it exists, otherwise returns None."""
    path = os.path.join(current_report_dir, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"[ERROR] Could not read {path}: {e}")
            return None
    return None

def extract_location_details(text):
    """Extracts location details from a given text."""
    result = {}
    for line in text.splitlines():
        if "Start Time:" in line:
            result["Time"] = line.strip().split("Start Time:")[-1].strip()
        elif "City:" in line:
            result["City"] = line.strip().split("City:")[-1].strip()
        elif "Region:" in line:
            result["State"] = line.strip().split("Region:")[-1].strip()
        elif "Country:" in line:
            result["Country"] = line.strip().split("Country:")[-1].strip()
    return result

def parse_application_report(file_path, top_n=5):
    """Parses application usage report and returns top N applications by duration."""
    usage = defaultdict(float)
    if not os.path.exists(file_path):
        print(f"[INFO] Application report not found: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Could not read application report {file_path}: {e}")
        return []

    merged_lines = []
    temp_line = ""
    for line in lines:
        if "Process:" in line and "Duration:" in line:
            merged_lines.append(line.strip())
        elif "Process:" in line:
            temp_line = line.strip()
        elif "Duration:" in line and temp_line:
            merged_lines.append(f"{temp_line} {line.strip()}")
            temp_line = ""

    pattern = r"Process:\s+(.*?),\s+Title:\s+(.*?),\s+Duration:\s+([\d.]+)"
    for line in merged_lines:
        match = re.search(pattern, line)
        if match:
            # Clean up process and title to avoid extraneous data (e.g., trailing commas)
            process = match.group(1).strip().split(',')[0].strip()
            title = match.group(2).strip().split(',')[0].strip()
            duration = float(match.group(3))
            key = f"{process} - {title}" if title else process # Use process only if title is empty
            usage[key] += duration

    return sorted(usage.items(), key=lambda x: x[1], reverse=True)[:top_n]

def parse_browser_report(file_path, top_n=5):
    """Parses browser usage report and returns top N URLs by duration."""
    usage = defaultdict(float)
    if not os.path.exists(file_path):
        print(f"[INFO] Browser report not found: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Could not read browser report {file_path}: {e}")
        return []

    merged_lines = []
    temp_line = ""
    for line in lines:
        if "Process:" in line and "Duration:" in line:
            merged_lines.append(line.strip())
        elif "Process:" in line:
            temp_line = line.strip()
        elif "Duration:" in line and temp_line:
            merged_lines.append(f"{temp_line} {line.strip()}")
            temp_line = ""

    pattern = r"Process:\s+(.*?),\s+URL:\s+(.*?),\s+Duration:\s+([\d.]+)"
    for line in merged_lines:
        match = re.search(pattern, line)
        if match:
            # Clean up process and URL to avoid extraneous data
            process = match.group(1).strip().split(',')[0].strip()
            url = match.group(2).strip().split(',')[0].strip()
            duration = float(match.group(3))
            key = f"{process} - {url}" # Keep both for browser context
            usage[key] += duration

    return sorted(usage.items(), key=lambda x: x[1], reverse=True)[:top_n]

def format_duration(seconds):
    """Formats duration in seconds to Hh Mm Ss string."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"

def shorten_label(text, max_length=40):
    """Shortens a string label for chart readability."""
    if len(text) <= max_length:
        return text
    return f"{text[:20]}...{text[-15:]}"

def make_unique_labels(data, max_length=40):
    """Generates unique labels for chart entries to avoid overlaps."""
    seen = {}
    result = []
    for entry, _ in data:
        # Take content after first ' - ' or the whole string if ' - ' not present
        label = entry.split(" - ", 1)[-1]
        short = label if len(label) <= max_length else f"{label[:(max_length-18)]}...{label[-15:]}"
        original_short = short
        counter = 1
        while short in seen:
            counter += 1
            # Append a counter, ensuring it still fits within max_length if possible
            short = f"{original_short[:max_length-len(str(counter))-3]}...({counter})"
            if len(short) > max_length: # Fallback for very short original_short + long counter
                short = f"{original_short[:max_length-len(str(counter))-3]}...({counter})" # Trim more aggressively
        seen[short] = True
        result.append(short)
    return result

def generate_bar_chart(data, output_path, title, label_type="full"):
    """Generates and saves a horizontal bar chart."""
    if not data:
        print(f"[INFO] No data to generate bar chart for: {title}")
        return False # Return False if no chart was generated

    labels = make_unique_labels(data)
    values = [duration for _, duration in data]

    # Ensure the directory exists before saving
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"[DEBUG] Created directory for bar chart: {output_dir}")
        except OSError as e:
            print(f"[ERROR] Failed to create directory for bar chart {output_dir}: {e}")
            return False

    fig, ax = plt.subplots(figsize=(10, max(5, len(labels) * 0.5))) # Adjust figure size based on number of bars, min 5
    ax.barh(labels, values, color='skyblue')
    ax.set_xlabel("Duration (seconds)")
    ax.set_title(title)
    ax.invert_yaxis() # Puts the highest value at the top
    plt.tight_layout()
    try:
        plt.savefig(output_path)
        print(f"[DEBUG] Bar chart generated at: {output_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not save bar chart {output_path}: {e}")
        return False
    finally:
        plt.close(fig) # Always close the figure to free up memory

def generate_pie_activity_track(current_pie_chart_path, active_time_val, idle_time_val):
    """Generates and saves a pie chart for active vs. idle time."""
    # Ensure active_time_val and idle_time_val are numeric and non-negative
    if not isinstance(active_time_val, (int, float)) or not isinstance(idle_time_val, (int, float)):
        print(f"[ERROR] Invalid input types for active_time_val or idle_time_val. Got {type(active_time_val)}, {type(idle_time_val)}.")
        return False
    if active_time_val < 0 or idle_time_val < 0:
        print(f"[ERROR] Negative time values are not allowed: active={active_time_val}, idle={idle_time_val}")
        return False

    if active_time_val + idle_time_val == 0:
        print("[INFO] No activity data to generate pie chart (active_time + idle_time is zero).")
        return False

    labels = ['Active Time', 'Idle Time']
    times = [active_time_val, idle_time_val]
    colors = ['#4CAF50', '#F44336'] # Green for active, Red for idle

    # Calculate percentages safely
    total_time = sum(times)
    # Handle potential division by zero if total_time somehow became 0 despite earlier check
    if total_time == 0:
        print("[ERROR] Total time is zero after sum calculation, cannot calculate percentages.")
        return False
    percentages = [f"{(t / total_time) * 100:.1f}%" for t in times]

    # Ensure the directory exists before saving
    output_dir = os.path.dirname(current_pie_chart_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"[DEBUG] Created directory for pie chart: {output_dir}")
        except OSError as e:
            print(f"[ERROR] Failed to create directory for pie chart {output_dir}: {e}")
            return False

    fig, ax = plt.subplots(figsize=(4, 4)) # Use object-oriented interface
    # wedgeprops=dict(width=0.4) creates a donut chart.
    wedges, texts = ax.pie(times, labels=None, colors=colors, startangle=140, wedgeprops=dict(width=0.4))
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.

    # Add text labels manually to avoid overlap
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(xycoords='data', textcoords='data', arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        # --- FIX for horizontalalignment ---
        if x > 0:
            horizontalalignment = "left"
        elif x < 0:
            horizontalalignment = "right"
        else: # x is 0 (vertical line)
            # You can choose 'center', 'right', or 'left' here based on preference
            # For donut charts, 'center' might work well or align based on y
            horizontalalignment = "center" # Default to center for vertical lines
            # Alternatively, if you want to align based on y for a vertical line:
            # horizontalalignment = "right" if y > 0 else "left"
        # --- END FIX ---

        connectionstyle = "angle,angleA=0,angleB={}".format(ang)

        # Check for NaN in coordinates, which can happen with certain data distributions
        if math.isnan(x) or math.isnan(y):
            continue # Skip annotating this wedge if coordinates are NaN

        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(percentages[i], xy=(x, y), xytext=(1.35*x, 1.35*y),
                                horizontalalignment=horizontalalignment, **kw)


    # Place the summary text below the pie chart
    plt.figtext(0.5, 0.01, f"{percentages[0]} Active on PC and {percentages[1]} Idle",
                ha="center", fontsize=10, fontweight='bold', wrap=True)

    plt.tight_layout(rect=[0, 0.1, 1, 1]) # Adjust layout to make space for figtext
    try:
        plt.savefig(current_pie_chart_path)
        print(f"[DEBUG] Pie chart generated at: {current_pie_chart_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not save pie chart {current_pie_chart_path}: {e}")
        return False
    finally:
        plt.close(fig) # Always close the figure to free up memory


def generate_html_report(current_report_dir, current_output_html, current_app_bar_path, current_browser_bar_path, current_pie_chart_path):
    """Generates the main HTML summary report."""
    now = datetime.now()
    date_time_str = now.strftime('%d-%m-%Y %I:%M %p')

    config_data = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error decoding JSON from config file {CONFIG_PATH}: {e}")
        except Exception as e:
            print(f"[ERROR] Error reading config file {CONFIG_PATH}: {e}")
    else:
        print(f"[WARNING] Configuration file not found at: {CONFIG_PATH}")

    # Ensure the output directory for the HTML report exists
    output_html_dir = os.path.dirname(current_output_html)
    if output_html_dir and not os.path.exists(output_html_dir):
        try:
            os.makedirs(output_html_dir)
            print(f"[DEBUG] Created directory for HTML report: {output_html_dir}")
        except OSError as e:
            print(f"[ERROR] Failed to create directory for HTML report {output_html_dir}: {e}")
            return # Exit if directory cannot be created

    try:
        with open(current_output_html, 'w', encoding='utf-8') as f:
            f.write(f"""
            <html><head>
                <title>Cubi-View Report</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background-color: #f9f9f9; color: #333; padding: 20px; }}
                    h2 {{ color: #3b3b98; text-align: center; }}
                    summary {{ cursor: pointer; font-size: 1.1em; font-weight: bold; color: #2c3e50; }}
                    details {{ background: #ffffff; padding: 15px 25px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 0 8px rgba(0,0,0,0.05); }}
                    ul {{ list-style-type: none; padding-left: 0; }}
                    li {{ margin-bottom: 5px; }}
                    .status-enabled {{ color: green; font-weight: bold; }}
                    .status-disabled {{ color: red; font-weight: bold; }}
                    img {{ display: block; margin: 10px auto; border: 1px solid #ddd; border-radius: 6px; max-width: 100%; height: auto; }}
                    pre {{ background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                </style>
            </head><body>
            <h2>Cubi-View Daily Report</h2>
            <p><b>Report generated on:</b> {date_time_str}</p>

            <details open><summary>Monitoring Configuration</summary><ul>
            """)

            if config_data:
                for key, value in config_data.items():
                    css_class = "status-enabled" if value else "status-disabled"
                    status = "Enabled" if value else "Disabled"
                    f.write(f"<li>{key.replace('_', ' ').title()}: <span class='{css_class}'>{status}</span></li>")
            else:
                f.write("<li><i>Configuration data not available or could not be loaded.</i></li>")

            f.write("</ul></details>")

            def add_optional_report(title, filename, summary_open=False):
                content = read_text_file_if_exists(current_report_dir, filename)
                if content:
                    tag = "open" if summary_open else ""
                    f.write(f"<details {tag}><summary>{title}</summary><pre>{content}</pre></details>")

            f.write(f"""
            <details open><summary>Activity Summary</summary>
            <p><b>Active Time:</b> {format_duration(active_time)}</p>
            <p><b>Idle Time:</b> {format_duration(idle_time)}</p>
            """)
            # Check if the pie chart file actually exists before embedding
            if os.path.exists(current_pie_chart_path):
                # Use a relative path if possible, or 'file:///' for absolute path if needed.
                # For local viewing, file:/// is generally reliable.
                f.write(f"<img src='file:///{os.path.abspath(current_pie_chart_path).replace(os.sep, '/')}' alt='Active vs Idle Pie Chart' width='300'>")
            else:
                f.write("<p><i>No active vs idle chart available.</i></p>")
            f.write("</details>")

            f.write(f"""
            <details open><summary>Input Summary</summary>
            <p><b>Keystrokes:</b> {total_keystrokes}</p>
            <p><b>Words Typed:</b> {total_words}</p>
            <p><b>Mouse Clicks:</b> {total_clicks}</p>
            </details>

            <details open><summary>Top Applications</summary><ul>
            """)
            if application_data:
                for app, dur in application_data:
                    f.write(f"<li>{app}: <b>{format_duration(dur)}</b></li>")
                # Check if the app bar chart file actually exists before embedding
                if os.path.exists(current_app_bar_path):
                    f.write(f"</ul><img src='file:///{os.path.abspath(current_app_bar_path).replace(os.sep, '/')}' alt='Top Applications' width='500'>")
                else:
                    f.write("<p><i>Top applications bar chart not available.</i></p>")
            else:
                f.write("<li><i>No application usage data.</i></li>")
            f.write("</details>")

            f.write(f"""
            <details open><summary>Top URLs</summary><ul>
            """)
            if browser_data:
                for url, dur in browser_data:
                    f.write(f"<li>{url}: <b>{format_duration(dur)}</b></li>")
                # Check if the browser bar chart file actually exists before embedding
                if os.path.exists(current_browser_bar_path):
                    f.write(f"</ul><img src='file:///{os.path.abspath(current_browser_bar_path).replace(os.sep, '/')}' alt='Top URLs' width='500'>")
                else:
                    f.write("<p><i>Top URLs bar chart not available.</i></p>")
            else:
                f.write("<li><i>No browser usage data.</i></li>")
            f.write("</details>")

            # Optional reports
            add_optional_report("Audio & Video Capture Log", "capture_report.txt")
            add_optional_report("Clipboard Activity", "clipboard_report.txt")
            add_optional_report("Install/Uninstall Log", "install-uninstall.txt")
            add_optional_report("Keylogger Report", "keylogger_report.txt")
            add_optional_report("Keystroke Summary", "keystroke_report.txt")
            add_optional_report("Lunch Restore Activity", "lunch_restore_report.txt")
            add_optional_report("Print Jobs Log", "print_job_report.txt")
            add_optional_report("Screenshot Capture Log", "screenshot_report.txt")

            loc_text = read_text_file_if_exists(current_report_dir, "location_report.txt")
            if loc_text:
                loc_data = extract_location_details(loc_text)
                f.write("<details><summary>Location Info (Based on IP address)</summary><ul>")
                if loc_data:
                    for k in ("Time", "City", "State", "Country"):
                        if k in loc_data:
                            f.write(f"<li><b>{k}:</b> {loc_data[k]}</li>")
                else:
                    f.write("<li><i>Location data could not be extracted.</i></li>")
                f.write("</ul></details>")

            f.write("</body></html>")

        print(f"[+] HTML report generated at: {current_output_html}")
    except Exception as e:
        print(f"[ERROR] Failed to write HTML report {current_output_html}: {e}")

def create_report_zip(report_dir, zip_filename):
    """
    Creates a zip file containing all files from the report directory.
    
    Args:
        report_dir (str): Path to the report directory to zip
        zip_filename (str): Path where the zip file should be created
    
    Returns:
        bool: True if zip creation was successful, False otherwise
    """
    try:
        html_report_logger.info(f"Creating zip file: {zip_filename} from directory: {report_dir}")
        
        # Check if source directory exists
        if not os.path.exists(report_dir):
            html_report_logger.error(f"Source directory does not exist: {report_dir}")
            return False
        
        # Count files to be zipped
        file_count = 0
        files_to_zip = []
        zip_filename_base = os.path.basename(zip_filename)
        
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip any zip files to avoid recursion
                if not file.endswith('.zip') and file_path != zip_filename:
                    files_to_zip.append((file_path, os.path.relpath(file_path, report_dir)))
                    file_count += 1
        
        html_report_logger.info(f"Found {file_count} files to zip")
        
        if file_count == 0:
            html_report_logger.warning(f"No files found in directory {report_dir} to zip")
            # Create an empty zip file with a note
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr('README.txt', 'This report directory was empty at the time of zip creation.')
            return True
        
        # Create the zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, arcname in files_to_zip:
                try:
                    zipf.write(file_path, arcname)
                    file_size = os.path.getsize(file_path)
                    html_report_logger.info(f"Added to zip: {arcname} ({file_size} bytes)")
                except Exception as e:
                    html_report_logger.error(f"Failed to add file {file_path} to zip: {e}")
                    continue
        
        # Verify the zip file was created and has content
        if os.path.exists(zip_filename):
            zip_size = os.path.getsize(zip_filename)
            html_report_logger.info(f"Successfully created zip file: {zip_filename} (Size: {zip_size} bytes)")
            
            # Verify zip file integrity
            try:
                with zipfile.ZipFile(zip_filename, 'r') as zipf:
                    zip_contents = zipf.namelist()
                    html_report_logger.info(f"Zip file contains {len(zip_contents)} files: {zip_contents}")
                return True
            except zipfile.BadZipFile:
                html_report_logger.error(f"Created zip file is corrupted: {zip_filename}")
                return False
        else:
            html_report_logger.error(f"Zip file was not created: {zip_filename}")
            return False
        
    except Exception as e:
        html_report_logger.error(f"Failed to create zip file {zip_filename}: {e}")
        return False

def upload_report_to_cloud(zip_file_path, system_id):
    """
    Uploads the report zip file to the cloud using the CubiView API.
    
    Args:
        zip_file_path (str): Path to the zip file to upload
        system_id (str): System ID for the device
    
    Returns:
        dict: Response with status and message
    """
    try:
        html_report_logger.info(f"Uploading report to cloud: {zip_file_path}")
        
        if not os.path.exists(zip_file_path):
            error_msg = f"Zip file not found: {zip_file_path}"
            html_report_logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        # Verify the file is actually a zip file
        zip_size = os.path.getsize(zip_file_path)
        html_report_logger.info(f"Zip file size: {zip_size} bytes")
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zipf:
                file_list = zipf.namelist()
                html_report_logger.info(f"Zip file verification successful. Contains {len(file_list)} files: {file_list[:5]}{'...' if len(file_list) > 5 else ''}")
        except zipfile.BadZipFile:
            error_msg = f"File is not a valid zip file: {zip_file_path}"
            html_report_logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        upload_url = "https://cubiview.onrender.com/api/device/report"
        
        # Prepare the files and data for upload with proper headers
        with open(zip_file_path, 'rb') as zip_file:
            # Read the file content to verify it's not empty
            zip_content = zip_file.read()
            if len(zip_content) == 0:
                error_msg = f"Zip file is empty: {zip_file_path}"
                html_report_logger.error(error_msg)
                return {"success": False, "message": error_msg}
            
            # Reset file pointer for upload
            zip_file.seek(0)
            
            # Use proper filename with timestamp for uniqueness
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CubiView_Report_{system_id}_{timestamp}.zip"
            
            files = {
                'reportZip': (filename, zip_file, 'application/zip')
            }
            data = {
                'systemId': system_id
            }
            
            # Add proper headers
            headers = {
                'User-Agent': 'CubiView-Client/1.0',
                'Accept': 'application/json'
            }
            
            html_report_logger.info(f"Uploading to {upload_url} with systemId: {system_id}")
            html_report_logger.info(f"Upload filename: {filename}")
            html_report_logger.info(f"Upload data size: {len(zip_content)} bytes")
            
            # Upload with timeout
            response = requests.post(
                upload_url,
                files=files,
                data=data,
                headers=headers,
                timeout=120  # 2 minute timeout for large files
            )
            
            html_report_logger.info(f"Upload response status: {response.status_code}")
            html_report_logger.info(f"Upload response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    html_report_logger.info(f"Upload successful: {response_data}")
                    return {
                        "success": True, 
                        "message": "Report uploaded successfully to cloud",
                        "response": response_data
                    }
                except json.JSONDecodeError:
                    html_report_logger.info("Upload successful (non-JSON response)")
                    html_report_logger.info(f"Response text: {response.text[:500]}...")
                    return {
                        "success": True, 
                        "message": "Report uploaded successfully to cloud",
                        "response": response.text
                    }
            else:
                error_msg = f"Upload failed with status {response.status_code}: {response.text}"
                html_report_logger.error(error_msg)
                return {"success": False, "message": error_msg}
                
    except requests.exceptions.Timeout:
        error_msg = "Upload timeout: Request to cloud server timed out"
        html_report_logger.error(error_msg)
        return {"success": False, "message": error_msg}
    except requests.exceptions.ConnectionError:
        error_msg = "Upload connection error: Could not connect to cloud server"
        html_report_logger.error(error_msg)
        return {"success": False, "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error during upload: {e}"
        html_report_logger.exception(error_msg)
        return {"success": False, "message": error_msg}

def main_html_report():
    """
    Main function to orchestrate the generation of the daily HTML report.
    Resets global report data, creates necessary directories, parses reports,
    generates charts, generates the HTML report, creates zip file, and uploads to cloud.
    Returns a dictionary with status, report path, report date, and a new 'has_data' flag.
    """
    global application_data, browser_data, active_time, idle_time # Ensure active_time and idle_time are globally accessible for parse_reports

    # Calculate report directory and file paths for the current date
    date_str = datetime.now().strftime("%d-%m-%Y")
    report_dir_for_today = os.path.join(REPORT_DIR, date_str)
    output_html_for_today = os.path.join(report_dir_for_today, "CubiView_Summary_Report.html")

    app_bar_path = os.path.join(report_dir_for_today, "app_bar.png")
    browser_bar_path = os.path.join(report_dir_for_today, "browser_bar.png")
    pie_chart_path = os.path.join(report_dir_for_today, "active_idle_pie.png")
    
    # Zip file path
    zip_file_path = os.path.join(report_dir_for_today, f"CubiView_Report_{date_str}.zip")

    try:
        os.makedirs(report_dir_for_today, exist_ok=True)
        print(f"[DEBUG] Ensured report directory exists: {report_dir_for_today}")
    except OSError as e:
        print(f"[ERROR] Failed to create report directory {report_dir_for_today}: {e}")
        return {
            "status": "error",
            "message": f"Failed to create report directory: {e}",
            "html_path": None,
            "report_date": date_str,
            "has_data": False,
            "zip_path": None,
            "cloud_upload": {"success": False, "message": "Report directory creation failed"}
        }

    try:
        parse_reports(report_dir_for_today)
        print(f"[DEBUG] Parsed general activity. Active: {active_time}s, Idle: {idle_time}s, Keystrokes: {total_keystrokes}")

        application_data[:] = parse_application_report(os.path.join(report_dir_for_today, "application_report.txt"))
        browser_data[:] = parse_browser_report(os.path.join(report_dir_for_today, "browser_report.txt"))
        print(f"[DEBUG] Parsed application data ({len(application_data)} entries) and browser data ({len(browser_data)} entries).")
    except Exception as e:
        print(f"[ERROR] Failed to parse reports: {e}")
        return {
            "status": "error",
            "message": f"Failed to parse reports: {e}",
            "html_path": None,
            "report_date": date_str,
            "has_data": False,
            "zip_path": None,
            "cloud_upload": {"success": False, "message": "Report parsing failed"}
        }

    # Determine if any meaningful data was found
    has_data = (active_time > 0 or idle_time > 0 or total_keystrokes > 0 or total_words > 0 or total_clicks > 0 or
                len(application_data) > 0 or len(browser_data) > 0)

    try:
        # Pass the actual active_time and idle_time values to the pie chart function
        bar_app_generated = generate_bar_chart(application_data, app_bar_path, "Top 5 Applications", label_type="title")
        bar_browser_generated = generate_bar_chart(browser_data, browser_bar_path, "Top 5 URLs", label_type="url")
        pie_chart_generated = generate_pie_activity_track(pie_chart_path, active_time, idle_time)

        generate_html_report(report_dir_for_today, output_html_for_today, app_bar_path, browser_bar_path, pie_chart_path)

        # Create zip file containing all report files
        html_report_logger.info("Starting zip file creation and cloud upload process...")
        
        # Ensure zip file doesn't already exist to avoid conflicts
        if os.path.exists(zip_file_path):
            try:
                os.remove(zip_file_path)
                html_report_logger.info(f"Removed existing zip file: {zip_file_path}")
            except Exception as e:
                html_report_logger.warning(f"Could not remove existing zip file: {e}")
        
        zip_success = create_report_zip(report_dir_for_today, zip_file_path)
        
        # Upload to cloud if zip creation was successful
        cloud_upload_result = {"success": False, "message": "Zip creation failed"}
        if zip_success:
            try:
                system_id = get_system_id()
                html_report_logger.info(f"Uploading report with system ID: {system_id}")
                cloud_upload_result = upload_report_to_cloud(zip_file_path, system_id)
                html_report_logger.info(f"Cloud upload result: {cloud_upload_result}")
            except Exception as e:
                cloud_upload_result = {"success": False, "message": f"Cloud upload error: {e}"}
                html_report_logger.error(f"Cloud upload failed: {e}")
        else:
            html_report_logger.error("Zip file creation failed, skipping cloud upload")

        return {
            "status": "success",
            "message": "Report generation process completed.",
            "html_path": output_html_for_today,
            "report_date": date_str,
            "has_data": has_data,
            "zip_path": zip_file_path if zip_success else None,
            "cloud_upload": cloud_upload_result
        }
    except Exception as e:
        print(f"[ERROR] Failed to generate charts or HTML report: {e}")
        return {
            "status": "error",
            "message": f"Failed to generate charts or HTML report: {e}",
            "html_path": None,
            "report_date": date_str,
            "has_data": False,
            "zip_path": None,
            "cloud_upload": {"success": False, "message": "Chart/HTML generation failed"}
        }

def refresh_html_report():
    """
    Refreshes the HTML report by calling main_html_report and returns its status and path.
    """
    print("[DEBUG] Refreshing HTML report...")
    result = main_html_report()

    # Small delay for file system to catch up, though generally not strictly necessary for local files
    time.sleep(0.1)

    if result.get("status") == "success" and os.path.exists(result.get("html_path", "")):
        print(f"[DEBUG] HTML report refreshed successfully. Path: {result['html_path']}")
        if result.get("zip_path") and os.path.exists(result["zip_path"]):
            print(f"[DEBUG] Zip file created successfully. Path: {result['zip_path']}")
        if result.get("cloud_upload", {}).get("success"):
            print(f"[DEBUG] Report uploaded to cloud successfully.")
        else:
            print(f"[DEBUG] Cloud upload status: {result.get('cloud_upload', {}).get('message', 'Unknown')}")
        return {
            "status": "success",
            "message": "Report loaded successfully.",
            "html_path": result['html_path'],
            "report_date": result['report_date'],
            "has_data": result['has_data'],
            "zip_path": result.get('zip_path'),
            "cloud_upload": result.get('cloud_upload', {"success": False, "message": "Not attempted"})
        }
    else:
        print(f"[ERROR] Failed to refresh HTML report. Reason: {result.get('message', 'Unknown error.')}")
        return {
            "status": "error",
            "message": result.get("message", "Report file not found or could not be generated."),
            "html_path": None,
            "report_date": datetime.now().strftime("%d-%m-%Y"),
            "has_data": False,
            "zip_path": None,
            "cloud_upload": {"success": False, "message": "Report generation failed"}
        }

# Example usage (for testing)
if __name__ == "__main__":
    # Create dummy credentials.py and some dummy report files for testing
    if not os.path.exists('credentials.py'):
        with open('credentials.py', 'w') as f:
            f.write("REPORT_DIR = 'test_reports'\n")
            f.write("CONFIG_PATH = 'test_config.json'\n")
    if not os.path.exists('test_config.json'):
        with open('test_config.json', 'w') as f:
            json.dump({
                "activity_tracking_enabled": True,
                "keystroke_logging_enabled": True,
                "screenshot_capture_enabled": False
            }, f)

    today_dir = datetime.now().strftime("%d-%m-%Y")
    test_report_dir = os.path.join('test_reports', today_dir)
    os.makedirs(test_report_dir, exist_ok=True)

    # Create dummy activity report
    with open(os.path.join(test_report_dir, 'activity_report.txt'), 'w') as f:
        f.write("Working Time: 3600 seconds\n") # 1 hour active
        f.write("Idle Time: 1800 seconds\n")    # 0.5 hours idle

    # Create dummy keystroke report
    with open(os.path.join(test_report_dir, 'keystroke_report.txt'), 'w') as f:
        f.write("Total Keystrokes: 1500\n")
        f.write("Total Words Typed: 250\n")

    # Create dummy mouse click report
    with open(os.path.join(test_report_dir, 'mouse_click_report.txt'), 'w') as f:
        f.write("Total Clicks: 500\n")

    # Create dummy application report
    with open(os.path.join(test_report_dir, 'application_report.txt'), 'w') as f:
        f.write("Process: chrome.exe, Title: Gmail - Google Chrome, Duration: 1200.5\n")
        f.write("Process: vscode.exe, Title: html_report.py - VS Code, Duration: 900.2\n")
        f.write("Process: firefox.exe, Title: MDN Web Docs, Duration: 600.8\n")
        f.write("Process: calc.exe, Title: Calculator, Duration: 50.0\n")
        f.write("Process: explorer.exe, Title: File Explorer, Duration: 150.0\n")

    # Create dummy browser report
    with open(os.path.join(test_report_dir, 'browser_report.txt'), 'w') as f:
        f.write("Process: chrome.exe, URL: https://www.google.com, Duration: 300.0\n")
        f.write("Process: chrome.exe, URL: https://chat.openai.com, Duration: 900.0\n")
        f.write("Process: firefox.exe, URL: https://developer.mozilla.org, Duration: 600.0\n")
        f.write("Process: chrome.exe, URL: https://docs.python.org, Duration: 150.0\n")
        f.write("Process: edge.exe, URL: https://bing.com, Duration: 50.0\n")

    # Create dummy location report
    with open(os.path.join(test_report_dir, 'location_report.txt'), 'w') as f:
        f.write("Start Time: 2025-07-13 10:00:00\n")
        f.write("City: Kakinada\n")
        f.write("Region: Andhra Pradesh\n")
        f.write("Country: India\n")

    print("\n--- Running refresh_html_report ---")
    report_status = refresh_html_report()
    print(f"Report Generation Status: {report_status['status']}")
    if report_status['status'] == 'success':
        print(f"HTML Report Path: {report_status['html_path']}")
        print(f"Report Date: {report_status['report_date']}")
        print(f"Has Data: {report_status['has_data']}")
        print(f"You can now open '{report_status['html_path']}' in a web browser.")
    else:
        print(f"Error Message: {report_status['message']}")