# backend/run_server.py

import sys
import os
import logging
from threading import Thread
from flask import jsonify, request

# Import the 'app' instance from your api.py
from new_api import app # This imports the Flask app instance initialized in api.py

# Configure logging for run_server.py
# This will log to stderr by default, which Electron can capture
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
server_logger = logging.getLogger('server_logger')

# Suppress default Flask/Werkzeug access logs to avoid clutter
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Define the port for the backend
BACKEND_PORT = 8000

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the Electron app to verify backend readiness.
    This route is added to the 'app' instance imported from api.py.
    """
    server_logger.info("Health check requested.")
    return jsonify({"status": "healthy", "message": "Flask backend is running!"}), 200

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """
    Endpoint to gracefully shut down the Flask server.
    This is called by the Electron main process when the app quits.
    This route is added to the 'app' instance imported from api.py.
    """
    server_logger.info("Shutdown requested.")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        server_logger.warning("Not running with Werkzeug server, cannot use werkzeug.server.shutdown.")
        return jsonify({"message": "Server cannot be shut down via this endpoint (not Werkzeug)."})
    else:
        func() # Call the Werkzeug shutdown function
        server_logger.info("Werkzeug server shutdown initiated.")
        return jsonify({"message": "Server shutting down..."})

# The home route from api.py will now be the default if you have one.
# If you need a specific root for run_server, you can add it here, but it might conflict
# with routes defined in api.py if they share the same path.
# For example, if you want a simple root for just the server:
# @app.route('/', methods=['GET'])
# def home_server():
#     return jsonify({"message": "Welcome to the Flask Backend (via run_server)!"})


def run_flask_app():
    """
    Runs the Flask application.
    """
    server_logger.info(f"Starting Flask backend on port {BACKEND_PORT}...")
    try:
        # Use 0.0.0.0 to make it accessible from localhost in Electron
        # debug=False for production, as debug mode can cause issues with PyInstaller and multiple processes
          app.run(host='0.0.0.0', port=BACKEND_PORT, debug=True)
    except Exception as e:
        server_logger.error(f"Failed to start Flask app: {e}")
        # Exit the process if the app fails to start
        sys.exit(1)

if __name__ == '__main__':
    # When packaged with PyInstaller, the console output might be redirected.
    # Ensure logs go to a file or are visible for debugging.
    print(f"Flask backend (run_server.py) starting up. PID: {os.getpid()}")
    run_flask_app()
