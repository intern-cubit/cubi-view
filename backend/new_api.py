# backend/api.py

import os
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import json
import logging
from get_systemID import get_system_id

# Configure logging for the API
# This will log to stderr by default, which Electron can capture
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger('api_logger')

from GUI_backend import (
    load_config, save_config, toggle_feature, start_monitoring, stop_monitoring,
    is_monitoring_running, load_activation_key, save_activation_key,
    get_local_version, get_remote_version, perform_full_update,
    save_smtp_credentials_file, send_test_email, load_sites, add_site, remove_site,
    load_whitelisted_installers, add_whitelisted_installer, remove_whitelisted_installer,
    load_user_info, get_system_info, get_smtp_credentials_file
)
from html_report import main_html_report # Only main_html_report is directly called by API routes
from credentials import (VERSION_URL, RELEASES_URL, LOGO_IMAGE, ACTIVATION_PATH,
                          WHITELIST_FILE, BLOCKLIST_FILE, WHITELIST_JSON,
                          LOCAL_VERSION_FILE, CONFIG_PATH, USER_ID_PATH, REPORT_DIR)
print("Importing modules...")
print(USER_ID_PATH)
from write_report import send_email_with_zip    

app = Flask(__name__)
CORS(app, origins=["*"])


# === CONFIG ===
@app.route('/api/config', methods=['GET'])
def api_load_config():
    app_logger.info("API: Loading config")
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def api_save_config():
    data = request.json
    app_logger.info(f"API: Saving config: {data}")
    save_config(data)
    return jsonify({"success": True})

@app.route('/api/toggle', methods=['POST'])
def api_toggle_feature():
    data = request.json
    if not data or 'features' not in data:
        app_logger.error("API: Invalid request data for toggling features.")
        return jsonify({"success": False, "message": "Invalid request data"}), 400
    features_to_update = data.get('features', {})
    app_logger.info(f"API: Toggling features: {features_to_update}")

    current_config = load_config()

    for feature_key, enabled_status in features_to_update.items():
        # Logic for mutually exclusive features
        if feature_key == "Website Whitelisting" and enabled_status:
            if current_config.get("Website Blocking"):
                current_config["Website Blocking"] = False
        elif feature_key == "Website Blocking" and enabled_status:
            if current_config.get("Website Whitelisting"):
                current_config["Website Whitelisting"] = False

        current_config[feature_key] = bool(enabled_status)

    app_logger.info(f"API: Updated config: {current_config}")
    save_config(current_config)
    return jsonify({"success": True})

# === AUTHENTICATION ===
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    if not data:
        app_logger.warning("API: Login attempt with invalid JSON data")
        return jsonify({"message": "Invalid JSON data"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        app_logger.warning("API: Login attempt with missing username or password")
        return jsonify({"message": "Username and password are required"}), 400

    try:
        app_logger.info(f"API: Attempting login for user: {username}")
        res = requests.post("https://api-keygen.obzentechnolabs.com/api/auth/login", json={
            "identifier": username,
            "password": password
        }, timeout=10)

        res_data = res.json()
        app_logger.info(f"API: External server login response status: {res.status_code}, data: {res_data}")

        if res.status_code == 200 and "token" in res_data and "user" in res_data:
            user = res_data["user"]
            token = res_data["token"]

            # Ensure REPORT_DIR exists before writing USER_ID_PATH
            if not os.path.exists(os.path.dirname(USER_ID_PATH)):
                os.makedirs(os.path.dirname(USER_ID_PATH), exist_ok=True)
                app_logger.info(f"Created directory for USER_ID_PATH: {os.path.dirname(USER_ID_PATH)}")


            with open(USER_ID_PATH, "w") as f:
                json.dump({
                    "user": user,
                    "token": token
                }, f, indent=4)
            app_logger.info(f"API: Login successful for {username}, user info saved.")
            return jsonify({
                "message": "Login successful",
                "user": user,
                "token": token
            }), 200
        else:
            error_message = res_data.get("message", "Login failed due to invalid credentials or an unknown error.")
            app_logger.warning(f"API: Login failed for {username}: {error_message}")
            return jsonify({"message": error_message}), res.status_code

    except requests.exceptions.Timeout:
        app_logger.error("API: Login connection timeout to authentication server.")
        return jsonify({"message": "Connection Error: Request to authentication server timed out."}), 504
    except requests.exceptions.ConnectionError:
        app_logger.error("API: Login connection error to authentication server.")
        return jsonify({"message": "Connection Error: Could not connect to the authentication server."}), 503
    except json.JSONDecodeError:
        app_logger.error("API: Received invalid JSON response from authentication server during login.")
        return jsonify({"message": "Error: Received invalid JSON response from authentication server."}), 500
    except Exception as e:
        app_logger.exception(f"API: An unexpected error occurred during login: {e}")
        return jsonify({"message": f"An internal server error occurred: {e}"}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json
    if not data:
        app_logger.warning("API: Forgot password attempt with invalid JSON data.")
        return jsonify({"message": "Invalid JSON data", "success": False}), 400

    email = data.get('email')

    if not email:
        app_logger.warning("API: Forgot password attempt with missing email.")
        return jsonify({"message": "Email is required", "success": False}), 400

    try:
        app_logger.info(f"API: Attempting forgot password for email: {email}")
        res = requests.post(
            "https://api-keygen.obzentechnolabs.com/api/auth/forgot-password",
            json={"email": email},
            timeout=10
        )

        res_data = res.json()
        app_logger.info(f"API: External forgot password server response (Status: {res.status_code}): {res_data}")

        if res.status_code == 200 and res_data.get("success"):
            app_logger.info(f"API: Forgot password request successful for {email}.")
            return jsonify({
                "message": "A reset link has been sent to your email.",
                "success": True
            }), 200
        else:
            error_message = res_data.get("message", "Failed to send reset email due to an unknown error.")
            app_logger.warning(f"API: Forgot password request failed for {email}: {error_message}")
            return jsonify({"message": error_message, "success": False}), res.status_code

    except requests.exceptions.Timeout:
        app_logger.error("API: Forgot password connection timeout to authentication server.")
        return jsonify({
            "message": "Connection Error: Request to authentication server timed out.",
            "success": False
        }), 504

    except requests.exceptions.ConnectionError:
        app_logger.error("API: Forgot password connection error to authentication server.")
        return jsonify({
            "message": "Connection Error: Could not connect to the authentication server.",
            "success": False
        }), 503

    except json.JSONDecodeError:
        app_logger.error("API: Received invalid JSON response from authentication server during forgot password.")
        return jsonify({
            "message": "Error: Received invalid JSON response from authentication server.",
            "success": False
        }), 500

    except Exception as e:
        app_logger.exception(f"API: An unexpected error occurred in forgot password endpoint: {e}")
        return jsonify({
            "message": f"An internal server error occurred: {e}",
            "success": False
        }), 500


# === REPORT HANDLING ===

@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    app_logger.info("API: Received request to generate report...")
    try:
        # Ensure REPORT_DIR exists before generating reports
        if not os.path.exists(REPORT_DIR):
            try:
                os.makedirs(REPORT_DIR, exist_ok=True)
                app_logger.info(f"Created base report directory: {REPORT_DIR}")
            except OSError as e:
                app_logger.critical(f"Could not create base report directory {REPORT_DIR}: {e}")
                return jsonify({"status": "error", "message": f"Server error: Could not create report directory: {e}"}), 500

        try:
            report_status = main_html_report() 
            if report_status.get("status") != "success":
                app_logger.error(f"Report generation failed: {report_status.get('message', 'Unknown error')}")
                return jsonify({"status": "error", "message": report_status.get("message", "Report generation failed.")}), 500
        except Exception as e:
            app_logger.exception(f"Error generating report: {e}")
            return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500
        app_logger.info(f"API: Report generation status: {report_status}")
        return jsonify(report_status)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/api/reports/daily-html', methods=['GET'])
def api_daily_html_metadata():
    app_logger.info("API: Received request for daily HTML report metadata...")
    # This route seems to trigger report generation. If it's just for metadata,
    # it should ideally read existing reports. For now, keeping as is per your code.
    report_status = main_html_report()
    app_logger.info(f"API: Daily HTML report metadata status: {report_status}")
    return jsonify(report_status)

@app.route('/api/reports/preview', methods=['GET'])
def api_reports_preview():
    app_logger.info("API: Received request for report HTML preview...")
    report_result = main_html_report() # This will generate a new report or get the latest one

    if report_result.get("status") == "success" and os.path.exists(report_result.get("html_path", "")):
        try:
            with open(report_result['html_path'], 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            app_logger.info(f"API: Serving HTML preview from {report_result['html_path']}")
            return Response(html_content, mimetype='text/html')
        except Exception as e:
            app_logger.exception(f"API: Failed to read HTML report for preview: {e}")
            return jsonify({"status": "error", "message": f"Failed to read report for preview: {e}"}), 500
    else:
        app_logger.warning(f"API: Report not found or could not be generated for preview: {report_result.get('message', 'Unknown error')}")
        return jsonify({"status": "error", "message": report_result.get("message", "Report not found or could not be generated.")}), 404

@app.route('/reports/view_dated/<date_folder>/<path:filename>', methods=['GET'])
def api_reports_view_dated(date_folder, filename):
    directory_to_serve = os.path.join(REPORT_DIR, date_folder)
    app_logger.info(f"API: Request to serve file '{filename}' from dated report directory: {directory_to_serve}")

    if not os.path.exists(directory_to_serve):
        app_logger.warning(f"API: Directory not found for dated report: {directory_to_serve}")
        return jsonify({"message": "Report not found for this date."}, 404)

    try:
        return send_from_directory(directory_to_serve, filename)
    except Exception as e:
        app_logger.exception(f"API: Failed to serve file {filename} from {directory_to_serve}: {e}")
        return jsonify({"message": f"Could not retrieve file: {e}"}), 500

# === MONITORING CONTROL ===
@app.route('/api/start', methods=['POST'])
def api_start_monitoring():
    app_logger.info("API: Starting monitoring")
    success = start_monitoring()
    return jsonify({"started": success})

@app.route('/api/stop', methods=['POST'])
def api_stop_monitoring():
    app_logger.info("API: Stopping monitoring")
    success = stop_monitoring()
    return jsonify({"stopped": success})

@app.route('/api/status', methods=['GET'])
def api_monitoring_status():
    running = is_monitoring_running()
    app_logger.info(f"API: Monitoring status: {running}")
    return jsonify({"running": running})

# === ACTIVATION ===
@app.route('/api/activation', methods=['GET'])
def api_get_activation():
    key = load_activation_key()
    app_logger.info(f"API: Getting activation key (exists: {bool(key)})")
    return jsonify({"activation_key": key})

@app.route('/api/activation', methods=['POST'])
def api_save_activation():
    systemId = get_system_id()
    key = request.json.get('activation_key')
    if not key or not systemId:
        app_logger.warning("API: Activation key is missing in request.")
        return jsonify({"message": "Activation key is required."}), 400
    try: 
        res = requests.post("https://api-keygen.obzentechnolabs.com/api/device/verify-device", json={
                "systemId": systemId,
                "activationKey": key,
                "appName": "Cubi-View"
            }, timeout=10)

        res_data = res.json()
        app_logger.info(f"API: External server login response status: {res.status_code}, data: {res_data}")

        if res.status_code == 200:
            app_logger.info(f"API: Saving activation key (length: {len(key) if key else 0})")
            success = save_activation_key(key)
            return jsonify({"success": success})
        else:
                error_message = res_data.get("message", "activation failed due to invalid activation key or an unknown error.")
                return jsonify({"message": error_message}), res.status_code

    except requests.exceptions.Timeout:
        app_logger.error("API: Login connection timeout to authentication server.")
        return jsonify({"message": "Connection Error: Request to authentication server timed out."}), 504
    except requests.exceptions.ConnectionError:
        app_logger.error("API: Login connection error to authentication server.")
        return jsonify({"message": "Connection Error: Could not connect to the authentication server."}), 503
    except json.JSONDecodeError:
        app_logger.error("API: Received invalid JSON response from authentication server during login.")
        return jsonify({"message": "Error: Received invalid JSON response from authentication server."}), 500
    except Exception as e:
        app_logger.exception(f"API: An unexpected error occurred during login: {e}")
        return jsonify({"message": f"An internal server error occurred: {e}"}), 500

# === VERSION ===
@app.route('/api/version/local', methods=['GET'])
def api_local_version():
    version = get_local_version()
    app_logger.info(f"API: Local version: {version}")
    return jsonify({"local_version": version})

@app.route('/api/version/remote', methods=['GET'])
def api_remote_version():
    version = get_remote_version()
    app_logger.info(f"API: Remote version: {version}")
    return jsonify({"remote_version": version})

@app.route('/api/update', methods=['POST'])
def api_update():
    version = request.json.get('version')
    app_logger.info(f"API: Performing update to version: {version}")
    updated_files = perform_full_update(version)
    return jsonify({"updated_files": updated_files})

# === SMTP ===
@app.route('/api/smtp/config', methods=['GET'])
def api_load_smtp_config():
    config = get_smtp_credentials_file()
    # Filter out sensitive information like password for API response
    config_safe = {k: v for k, v in config.items() if k != 'password'}
    app_logger.info("API: Loading SMTP config (password omitted)")
    return jsonify(config_safe)

@app.route('/api/smtp/save', methods=['POST'])
def api_save_smtp():
    data = request.json
    if not data:
        app_logger.error("API: No JSON data received for SMTP save.")
        return jsonify({"success": False, "message": "No data provided."}), 400

    required_fields = ['email', 'password', 'recipient_email', 'smtp_server', 'smtp_port']
    if not all(field in data for field in required_fields):
        app_logger.error(f"API: Missing required fields for SMTP save. Received: {data.keys()}")
        return jsonify({"success": False, "message": "Missing required SMTP configuration fields."}), 400

    app_logger.info(f"API: Saving SMTP config for {data.get('email')}")
    try:
        save_smtp_credentials_file(
            data['email'],
            data['password'],
            data['recipient_email'],
            data.get('cc1', ''),
            data.get('cc2', ''),
            data['smtp_server'],
            data['smtp_port']
        )
        return jsonify({"success": True, "message": "SMTP settings saved successfully."})
    except Exception as e:
        app_logger.error(f"API: Error saving SMTP credentials: {e}")
        return jsonify({"success": False, "message": f"Error saving SMTP settings: {str(e)}"}), 500

@app.route('/api/smtp/send-test', methods=['POST'])
def api_send_test_email():
    data = request.json
    if not data:
        app_logger.error("API: No JSON data received for test email.")
        return jsonify({"success": False, "message": "No data provided for test email."}), 400

    required_fields = ['email', 'password', 'recipient_email', 'smtp_server', 'smtp_port']
    if not all(field in data for field in required_fields):
        app_logger.error(f"API: Missing required fields for test email. Received: {data.keys()}")
        return jsonify({"success": False, "message": "Missing required fields for sending test email."}), 400

    recipient_email = data.get('recipient_email')
    app_logger.info(f"API: Attempting to send test email to {recipient_email}")

    # Pass the entire config data to the helper function
    success, message = send_test_email(data)
    if success:
        app_logger.info(f"API: Test email sent successfully to {recipient_email}.")
    else:
        app_logger.error(f"API: Failed to send test email to {recipient_email}: {message}")
    return jsonify({"success": success, "message": message})

# === REPORTS: SEND VIA EMAIL ===
@app.route('/api/reports/send_email', methods=['POST'])
def send_report_email_api():
    data = request.json
    recipient_email = data.get('recipient_email')
    app_logger.info(f"API: Request to send report email to {recipient_email}")

    if not recipient_email:
        app_logger.warning("API: Send report email failed: Recipient email is required.")
        return jsonify({"message": "Recipient email is required."}, 400)

    try:
        # Ensure REPORT_DIR exists before generating reports
        if not os.path.exists(REPORT_DIR):
            os.makedirs(REPORT_DIR, exist_ok=True)
            app_logger.info(f"Created base report directory for email send: {REPORT_DIR}")

        report_result = main_html_report() # Generate the report first
        if report_result['status'] != 'success':
            app_logger.error(f"API: Failed to generate report before sending email: {report_result['message']}")
            return jsonify({"message": f"Failed to generate report before sending: {report_result['message']}"}, 500)

        current_output_html = report_result['html_path']
        current_report_dir = os.path.dirname(current_output_html)

        smtp_config_loaded = get_smtp_credentials_file()
        if not smtp_config_loaded or not smtp_config_loaded.get('email') or not smtp_config_loaded.get('password'):
            app_logger.warning("API: SMTP credentials not configured for sending email.")
            return jsonify({"message": "SMTP credentials not configured. Please set them up in GUI."}, 400)

        success, message = send_email_with_zip(
            sender_email=smtp_config_loaded.get('email'),
            sender_password=smtp_config_loaded.get('password'),
            smtp_server=smtp_config_loaded.get('smtp_server'),
            smtp_port=smtp_config_loaded.get('smtp_port'),
            recipient_email=recipient_email,
            zip_file_path=current_report_dir, # This should be the directory containing the report and its assets
            html_report_path=current_output_html
        )
        if success:
            app_logger.info(f"API: Report email sent successfully to {recipient_email}.")
            return jsonify({"message": message})
        else:
            app_logger.error(f"API: Failed to send report email to {recipient_email}: {message}")
            return jsonify({"message": message}, 500)
    except Exception as e:
        app_logger.exception(f"API: An error occurred while sending the report email: {e}")
        return jsonify({"message": f"An error occurred while sending the report email: {str(e)}"}, 500)

# === WEBSITE WHITELIST ===
@app.route('/api/whitelist', methods=['GET'])
def api_get_whitelist():
    try:
        sites = load_sites(WHITELIST_FILE)
        app_logger.info(f"API: Getting whitelist ({len(sites)} sites)")
        app_logger.info(f"API: Sites: {sites}")
        return jsonify({"whitelist": sites}), 200
    except (IOError, ValueError) as e:
        app_logger.error(f"Error getting whitelist: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/whitelist', methods=['POST'])
def api_add_whitelist():
    site = request.json.get('site')
    if not site:
        return jsonify({"error": "Missing 'site' in request body"}), 400
    try:
        app_logger.info(f"API: Adding to whitelist: {site}")
        sites = add_site(WHITELIST_FILE, site)
        return jsonify({"message": f"Site '{site}' added to whitelist.", "whitelist": sites}), 200
    except (IOError, ValueError) as e:
        app_logger.error(f"Error adding to whitelist: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/whitelist', methods=['DELETE'])
def api_remove_whitelist():
    site = request.json.get('site')
    if not site:
        return jsonify({"error": "Missing 'site' in request body"}), 400
    try:
        app_logger.info(f"API: Removing from whitelist: {site}")
        sites_before_removal = load_sites(WHITELIST_FILE) # Load before removal to check if it existed
        sites = remove_site(WHITELIST_FILE, site)
        if site not in sites_before_removal:
             return jsonify({"message": f"Site '{site}' was not found in the whitelist.", "whitelist": sites}), 404
        return jsonify({"message": f"Site '{site}' removed from whitelist.", "whitelist": sites}), 200
    except (IOError, ValueError) as e:
        app_logger.error(f"Error removing from whitelist: {e}")
        return jsonify({"error": str(e)}), 500

# === BLOCKLIST ===
@app.route('/api/blocklist', methods=['GET'])
def api_get_blocklist():
    try:
        sites = load_sites(BLOCKLIST_FILE)
        app_logger.info(f"API: Getting blocklist ({len(sites)} sites)")
        return jsonify({"blocklist": sites}), 200
    except (IOError, ValueError) as e:
        app_logger.error(f"Error getting blocklist: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/blocklist', methods=['POST'])
def api_add_blocklist():
    site = request.json.get('site')
    if not site:
        return jsonify({"error": "Missing 'site' in request body"}), 400
    try:
        app_logger.info(f"API: Adding to blocklist: {site}")
        sites = add_site(BLOCKLIST_FILE, site)
        return jsonify({"message": f"Site '{site}' added to blocklist.", "blocklist": sites}), 200
    except (IOError, ValueError) as e:
        app_logger.error(f"Error adding to blocklist: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/blocklist', methods=['DELETE'])
def api_remove_blocklist():
    site = request.json.get('site')
    if not site:
        return jsonify({"error": "Missing 'site' in request body"}), 400
    try:
        app_logger.info(f"API: Removing from blocklist: {site}")
        sites_before_removal = load_sites(BLOCKLIST_FILE) # Load before removal to check if it existed
        sites = remove_site(BLOCKLIST_FILE, site)
        if site not in sites_before_removal:
             return jsonify({"message": f"Site '{site}' was not found in the blocklist.", "blocklist": sites}), 404
        return jsonify({"message": f"Site '{site}' removed from blocklist.", "blocklist": sites}), 200
    except (IOError, ValueError) as e:
        app_logger.error(f"Error removing from blocklist: {e}")
        return jsonify({"error": str(e)}), 500

# === INSTALLER WHITELIST ===
@app.route('/api/installers', methods=['GET'])
def api_get_installers():
    installers = load_whitelisted_installers()
    app_logger.info(f"API: Getting installers ({len(installers)} installers)")
    return jsonify({"installers": installers})

@app.route('/api/installers', methods=['POST'])
def api_add_installer():
    name = request.json.get('name')
    app_logger.info(f"API: Adding installer: {name}")
    installers = add_whitelisted_installer(name)
    return jsonify({"installers": installers})

@app.route('/api/installers', methods=['DELETE'])
def api_remove_installer():
    name = request.json.get('name')
    app_logger.info(f"API: Removing installer: {name}")
    installers = remove_whitelisted_installer(name)
    return jsonify({"installers": installers})

# === SYSTEM INFO & USER ===
@app.route('/api/user', methods=['GET'])
def api_user_info():
    user_info = load_user_info()
    app_logger.info("API: Getting user info")
    return jsonify(user_info)

@app.route('/api/system', methods=['GET'])
def api_system_info():
    system_info = get_system_info()
    app_logger.info("API: Getting system info")
    app_logger.info(f"API: System ID: {system_info.get('system_id', 'Unknown')}")
    return jsonify(system_info)

# === HEALTH CHECK ===
@app.route('/api/ping', methods=['GET'])
def api_ping():
    app_logger.info("API: Ping received")
    return jsonify({"message": "pong"})

# if __name__ == '__main__':

#     if not os.path.exists(REPORT_DIR):

#         try:

#             os.makedirs(REPORT_DIR, exist_ok=True)

#             print(f"Created base report directory: {REPORT_DIR}")

#         except OSError as e:

#             print(f"[CRITICAL ERROR] Could not create base report directory {REPORT_DIR}: {e}")

#     app.run(port=5000, debug=True)

if __name__ == '__main__':
    # print(api_get_whitelist())
    # print(api_get_blocklist())
    # print(api_system_info())
    # with app.app_context():
    #     print(api_get_whitelist())
    #     print(api_get_blocklist())
    #     print(api_system_info())
    app.run(port=8000, debug=True)