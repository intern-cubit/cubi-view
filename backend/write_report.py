import os
from datetime import datetime
from typing import List, Union
import zipfile
from credentials import REPORT_DIR
from PIL import Image
import textwrap
from credentials import SMTP_CREDENTIALS_FILE


def write_report(directory: str,
                 base_filename: str,
                 content: Union[str, List[str]],
                 title: str = None,
                 with_timestamp: bool = True,
                 mode: str = 'a',
                 wrap_width: int = 70):  # <-- new param
    """
    Universal report writer that creates/updates a report file.

    :param directory: Base folder (e.g., "logs"). Reports will be grouped into date-based subfolders.
    :param base_filename: File base name (e.g., "install-uninstall", "mouse_click_report").
    :param content: A string or list of strings to write to the file.
    :param title: Optional title/header for the report.
    :param with_timestamp: Whether to prefix each entry with a timestamp.
    :param mode: 'a' to append or 'w' to overwrite the file.
    :param wrap_width: Maximum characters per line before wrapping.
    """

    date_str = datetime.now().strftime("%d-%m-%Y")
    dated_directory = os.path.join(directory, date_str)
    os.makedirs(dated_directory, exist_ok=True)

    full_filename = f"{base_filename}.txt"
    filepath = os.path.join(dated_directory, full_filename)

    timestamp_format = "[%Y-%m-%d %H:%M:%S]"

    with open(filepath, mode, encoding="utf-8") as f:
        if mode == 'w' and title:
            f.write(f"{title}\n{'=' * 50}\n")

        if isinstance(content, list):
            for entry in content:
                wrapped_lines = textwrap.wrap(entry, width=wrap_width)
                for line in wrapped_lines:
                    if with_timestamp:
                        f.write(f"{datetime.now().strftime(timestamp_format)} {line}\n")
                    else:
                        f.write(f"{line}\n")
        else:
            wrapped_lines = textwrap.wrap(content, width=wrap_width)
            for line in wrapped_lines:
                if with_timestamp:
                    f.write(f"{datetime.now().strftime(timestamp_format)} {line}\n")
                else:
                    f.write(f"{line}\n")

    print(f"[✓] Report saved to {filepath}")



############### Create a Folder for Daily reports and Zip it ###########################


def zip_folder():
    # Step 1: Build today's dated folder path
    today_str = datetime.now().strftime("%d-%m-%Y")
    folder_path = os.path.join(REPORT_DIR, today_str)
    screenshots_folder = os.path.join(folder_path, "Screenshots")
    pdf_path = os.path.join(folder_path, "Screenshots.pdf")
    zip_path = folder_path + ".zip"

    if not os.path.exists(folder_path):
        print(f"[!] Folder does not exist: {folder_path}")
        return

    # Step 2: Convert screenshots to PDF
    if os.path.exists(screenshots_folder):
        images = []
        for file in sorted(os.listdir(screenshots_folder)):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(screenshots_folder, file)
                try:
                    img = Image.open(img_path).convert("RGB")
                    images.append(img)
                except Exception as e:
                    print(f"Error opening image {img_path}: {e}")
        if images:
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            print(f"[✓] PDF created at: {pdf_path}")
        else:
            print("[!] No screenshots found to convert.")
    else:
        print("[!] Screenshots folder not found. Skipping PDF generation.")

    # Step 3: Delete existing ZIP if it exists
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
            print(f"[✓] Existing zip deleted: {zip_path}")
        except Exception as e:
            print(f"Error deleting existing zip file {zip_path}: {e}")
            return None

    # Step 4: Create zip archive
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                # Skip the Screenshots folder
                if "Screenshots" in os.path.relpath(root, folder_path):
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        print(f"[✓] Zipped folder saved to: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"Error creating zip archive: {e}")
        return None


#################  Send Email #######################

import smtplib
import ssl
from email.message import EmailMessage
from tkinter import messagebox

def send_email_with_zip(from_addr, password, to_addr, subject, body, attachment_path, cc_list=None,
                        smtp_server_add="smtp.gmail.com", smtp_port_add =465):
    try:
        msg = EmailMessage()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)

        # Handle CC if any
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)

        # Attach ZIP file if it exists
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype="application", subtype="zip", filename=file_name)
        elif attachment_path:
            print(f"Attachment Missing: ZIP file not found: {attachment_path}. Email will be sent without attachment.")

        # Combine all recipients
        all_recipients = [to_addr] + (cc_list if cc_list else [])

        # Connect to custom SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server_add, smtp_port_add, context=context) as server:
            server.login(from_addr, password)
            server.send_message(msg, to_addrs=all_recipients)

        print(f"Email sent successfully to {to_addr}" + (f" and CC: {', '.join(cc_list)}" if cc_list else ""))
        return True, "Email sent successfully."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False, f"Failed to send email: {e}"

def load_smtp_credentials(filepath=SMTP_CREDENTIALS_FILE):
    creds = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split("=", 1)
                    creds[key] = value
    return (
        creds.get("from_email", ""),
        creds.get("password", ""),
        creds.get("to_email", ""),
        creds.get("cc1", ""),
        creds.get("cc2", ""),
        creds.get("smtp_server", ""),
        creds.get("smtp_port", "")
    )

