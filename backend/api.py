# backend/api.py

import os
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import json
from html_report import main_html_report # Only main_html_report is directly called by API routes

from GUI_backend import (
    load_config, save_config, toggle_feature, start_monitoring, stop_monitoring,
    is_monitoring_running, load_activation_key, save_activation_key,
    get_local_version, get_remote_version, perform_full_update,
    save_smtp_credentials_file, send_test_email, load_sites, add_site, remove_site,
    load_whitelisted_installers, add_whitelisted_installer, remove_whitelisted_installer,
    load_user_info, get_system_info, get_smtp_credentials_file
)

from credentials import (VERSION_URL, RELEASES_URL, LOGO_IMAGE, ACTIVATION_PATH,
                         WHITELIST_FILE, BLOCKLIST_FILE, WHITELIST_JSON,
                         LOCAL_VERSION_FILE, CONFIG_PATH, USER_ID_PATH, REPORT_DIR)
from write_report import send_email_with_zip

app = Flask(__name__)
CORS(app)

# === CONFIG ===
@app.route('/api/config', methods=['GET'])
def api_load_config():
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def api_save_config():
    data = request.json
    save_config(data)
    return jsonify({"success": True})

@app.route('/api/toggle', methods=['POST'])
def api_toggle_feature():
    data = request.json
    features_to_update = data.get('features', {})

    current_config = load_config()

    for feature_key, enabled_status in features_to_update.items():
        if feature_key == "Website Whitelisting" and enabled_status:
            if current_config.get("Website Blocking"):
                current_config["Website Blocking"] = False
        elif feature_key == "Website Blocking" and enabled_status:
            if current_config.get("Website Whitelisting"):
                current_config["Website Whitelisting"] = False

        current_config[feature_key] = bool(enabled_status)

    save_config(current_config)
    return jsonify({"success": True})

# === AUTHENTICATION ===
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    if not data:
        return jsonify({"message": "Invalid JSON data"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        # res = requests.post("https://api-keygen.obzentechnolabs.com/api/auth/login", json={
        #     "identifier": username,
        #     "password": password
        # }, timeout=10)

        res = requests.post("https://cubiview.onrender.com/api/auth/login", json={
            "identifier": username,
            "password": password
        }, timeout=10)

        res_data = res.json()
        print("External server response:", res_data)

        if res.status_code == 200 and "token" in res_data and "user" in res_data:
            user = res_data["user"]
            token = res_data["token"]

            with open(USER_ID_PATH, "w") as f:
                json.dump({
                    "user": user,
                    "token": token
                }, f, indent=4)

            return jsonify({
                "message": "Login successful",
                "user": user,
                "token": token
            }), 200
        else:
            error_message = res_data.get("message", "Login failed due to invalid credentials or an unknown error.")
            return jsonify({"message": error_message}), res.status_code

    except requests.exceptions.Timeout:
        return jsonify({"message": "Connection Error: Request to authentication server timed out."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"message": "Connection Error: Could not connect to the authentication server."}), 503
    except json.JSONDecodeError:
        return jsonify({"message": "Error: Received invalid JSON response from authentication server."}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"message": f"An internal server error occurred: {e}"}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json
    if not data:
        return jsonify({"message": "Invalid JSON data", "success": False}), 400

    email = data.get('email')

    if not email:
        return jsonify({"message": "Email is required", "success": False}), 400

    try:
        # res = requests.post(
        #     "https://api-keygen.obzentechnolabs.com/api/auth/forgot-password",
        #     json={"email": email},
        #     timeout=10
        # )

        res = requests.post(
            "https://cubiview.onrender.com/api/auth/forgot-password",
            json={"email": email},
            timeout=10
        )

        res_data = res.json()
        print(f"External forgot password server response (Status: {res.status_code}): {res_data}")

        if res.status_code == 200 and res_data.get("success"):
            return jsonify({
                "message": "A reset link has been sent to your email.",
                "success": True
            }), 200
        else:
            error_message = res_data.get("message", "Failed to send reset email due to an unknown error.")
            return jsonify({"message": error_message, "success": False}), res.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "message": "Connection Error: Request to authentication server timed out.",
            "success": False
        }), 504

    except requests.exceptions.ConnectionError:
        return jsonify({
            "message": "Connection Error: Could not connect to the authentication server.",
            "success": False
        }), 503

    except json.JSONDecodeError:
        return jsonify({
            "message": "Error: Received invalid JSON response from authentication server.",
            "success": False
        }), 500

    except Exception as e:
        print(f"An unexpected error occurred in forgot password endpoint: {e}")
        return jsonify({
            "message": f"An internal server error occurred: {e}",
            "success": False
        }), 500


# === REPORT HANDLING ===

@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    print("Received request to generate report...")
    report_status = main_html_report()
    return jsonify(report_status)

@app.route('/api/reports/daily-html', methods=['GET'])
def api_daily_html_metadata():
    print("Received request for daily HTML report metadata...")
    report_status = main_html_report()
    return jsonify(report_status)

@app.route('/api/reports/preview', methods=['GET'])
def api_reports_preview():
    print("Received request for report HTML preview...")
    report_result = main_html_report()

    if report_result.get("status") == "success" and os.path.exists(report_result.get("html_path", "")):
        try:
            with open(report_result['html_path'], 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            return Response(html_content, mimetype='text/html')
        except Exception as e:
            print(f"[ERROR] Failed to read HTML report for preview: {e}")
            return jsonify({"status": "error", "message": f"Failed to read report for preview: {e}"}), 500
    else:
        return jsonify({"status": "error", "message": report_result.get("message", "Report not found or could not be generated.")}), 404

@app.route('/reports/view_dated/<date_folder>/<path:filename>', methods=['GET'])
def api_reports_view_dated(date_folder, filename):
    directory_to_serve = os.path.join(REPORT_DIR, date_folder)

    if not os.path.exists(directory_to_serve):
        print(f"[ERROR] Directory not found: {directory_to_serve}")
        return jsonify({"message": "Report not found for this date."}, 404)

    try:
        return send_from_directory(directory_to_serve, filename)
    except Exception as e:
        print(f"[ERROR] Failed to serve file {filename} from {directory_to_serve}: {e}")
        return jsonify({"message": f"Could not retrieve file: {e}"}), 500

# === MONITORING CONTROL ===
@app.route('/api/start', methods=['POST'])
def api_start_monitoring():
    success = start_monitoring()
    return jsonify({"started": success})

@app.route('/api/stop', methods=['POST'])
def api_stop_monitoring():
    success = stop_monitoring()
    return jsonify({"stopped": success})

@app.route('/api/status', methods=['GET'])
def api_monitoring_status():
    running = is_monitoring_running()
    return jsonify({"running": running})

# === ACTIVATION ===
@app.route('/api/activation', methods=['GET'])
def api_get_activation():
    return jsonify({"activation_key": load_activation_key()})

@app.route('/api/activation', methods=['POST'])
def api_save_activation():
    key = request.json.get('activation_key')
    success = save_activation_key(key)
    return jsonify({"success": success})

# === VERSION ===
@app.route('/api/version/local', methods=['GET'])
def api_local_version():
    return jsonify({"local_version": get_local_version()})

@app.route('/api/version/remote', methods=['GET'])
def api_remote_version():
    version = get_remote_version()
    return jsonify({"remote_version": version})

@app.route('/api/update', methods=['POST'])
def api_update():
    version = request.json.get('version')
    updated_files = perform_full_update(version)
    return jsonify({"updated_files": updated_files})

# === SMTP ===
@app.route('/api/smtp/config', methods=['GET'])
def api_load_smtp_config():
    config = get_smtp_credentials_file()
    config_safe = {k: v for k, v in config.items() if k != 'password'}
    return jsonify(config_safe)

@app.route('/api/smtp/save', methods=['POST'])
def api_save_smtp():
    data = request.json
    save_smtp_credentials_file(
        data['email'], data['password'], data['recipient_email'], # Re-aligned with typical usage
        data.get('cc1', ''), data.get('cc2', ''), data['smtp_server'], data['smtp_port']
    )
    return jsonify({"success": True})

@app.route('/api/smtp/send-test', methods=['POST'])
def api_send_test_email():
    data = request.json
    recipient_email = data.get('recipient_email')
    success, message = send_test_email(recipient_email)
    return jsonify({"success": success, "message": message})

# === REPORTS: SEND VIA EMAIL ===
@app.route('/api/reports/send_email', methods=['POST'])
def send_report_email_api():
    data = request.json
    recipient_email = data.get('recipient_email')
    if not recipient_email:
        return jsonify({"message": "Recipient email is required."}, 400)

    try:
        report_result = main_html_report()
        if report_result['status'] != 'success':
            return jsonify({"message": f"Failed to generate report before sending: {report_result['message']}"}, 500)

        current_output_html = report_result['html_path']
        current_report_dir = os.path.dirname(current_output_html)

        smtp_config_loaded = get_smtp_credentials_file()
        if not smtp_config_loaded:
             return jsonify({"message": "SMTP credentials not configured. Please set them up in GUI."}, 400)

        success, message = send_email_with_zip(
            sender_email=smtp_config_loaded.get('email'),
            sender_password=smtp_config_loaded.get('password'),
            smtp_server=smtp_config_loaded.get('smtp_server'),
            smtp_port=smtp_config_loaded.get('smtp_port'),
            recipient_email=recipient_email,
            zip_file_path=current_report_dir,
            html_report_path=current_output_html
        )
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"message": message}, 500)
    except Exception as e:
        return jsonify({"message": f"An error occurred while sending the report email: {str(e)}"}, 500)

# === WEBSITE WHITELIST ===
@app.route('/api/whitelist', methods=['GET'])
def api_get_whitelist():
    return jsonify({"whitelist": load_sites(WHITELIST_FILE)})

@app.route('/api/whitelist', methods=['POST'])
def api_add_whitelist():
    site = request.json.get('site')
    sites = add_site(WHITELIST_FILE, site)
    return jsonify({"whitelist": sites})

@app.route('/api/whitelist', methods=['DELETE'])
def api_remove_whitelist():
    site = request.json.get('site')
    sites = remove_site(WHITELIST_FILE, site)
    return jsonify({"whitelist": sites})

# === BLOCKLIST ===
@app.route('/api/blocklist', methods=['GET'])
def api_get_blocklist():
    return jsonify({"blocklist": load_sites(BLOCKLIST_FILE)})

@app.route('/api/blocklist', methods=['POST'])
def api_add_blocklist():
    site = request.json.get('site')
    sites = add_site(BLOCKLIST_FILE, site)
    return jsonify({"blocklist": sites})

@app.route('/api/blocklist', methods=['DELETE'])
def api_remove_blocklist():
    site = request.json.get('site')
    sites = remove_site(BLOCKLIST_FILE, site)
    return jsonify({"blocklist": sites})

# === INSTALLER WHITELIST ===
@app.route('/api/installers', methods=['GET'])
def api_get_installers():
    return jsonify({"installers": load_whitelisted_installers()})

@app.route('/api/installers', methods=['POST'])
def api_add_installer():
    name = request.json.get('name')
    installers = add_whitelisted_installer(name)
    return jsonify({"installers": installers})

@app.route('/api/installers', methods=['DELETE'])
def api_remove_installer():
    name = request.json.get('name')
    installers = remove_whitelisted_installer(name)
    return jsonify({"installers": installers})

# === SYSTEM INFO & USER ===
@app.route('/api/user', methods=['GET'])
def api_user_info():
    return jsonify(load_user_info())

@app.route('/api/system', methods=['GET'])
def api_system_info():
    return jsonify(get_system_info())

# === HEALTH CHECK ===
@app.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify({"message": "pong"})

# === MAIN ===
if __name__ == '__main__':
    if not os.path.exists(REPORT_DIR):
        try:
            os.makedirs(REPORT_DIR, exist_ok=True)
            print(f"Created base report directory: {REPORT_DIR}")
        except OSError as e:
            print(f"[CRITICAL ERROR] Could not create base report directory {REPORT_DIR}: {e}")
    app.run(port=5000, debug=True)