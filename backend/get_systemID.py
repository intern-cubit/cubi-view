# get_system_id.py
import hashlib
import wmi
import subprocess
import os
from credentials import REPORT_DIR

def get_motherboard_serial():
    try:
        try:
            result = subprocess.check_output(
                ["powershell.exe", "-Command", "(Get-WmiObject Win32_BaseBoard).SerialNumber"],
                text=True,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            serial = result.strip()
            if serial:
                return serial
            else:
                print("Powershell returned empty motherboard serial. Falling back to wmic.")
        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            print(f"Powershell WMI query for motherboard serial failed ({e}). Falling back to wmic.")

        result = subprocess.check_output("wmic baseboard get serialnumber", shell=True, text=True)
        serial = result.split('\n')[1].strip()
        return serial
    except Exception as e:
        print(f"Failed to get motherboard serial: {e}")
        return f"Error getting motherboard serial: {e}"

def get_processor_id():
    try:
        try:
            result = subprocess.check_output(
                ["powershell.exe", "-Command", "(Get-WmiObject Win32_Processor).ProcessorId"],
                text=True,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            processor_id = result.strip()
            if processor_id:
                return processor_id
            else:
                print("Powershell returned empty processor ID. Falling back to wmic.")
        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            print(f"Powershell WMI query for processor ID failed ({e}). Falling back to wmic.")

    except Exception as e:
        print(f"Initial attempt for processor ID failed. Falling back to wmic. Error: {e}")
    try:
        result = subprocess.check_output("wmic cpu get processorId", shell=True, text=True)
        processor_id = result.split('\n')[1].strip()
        return processor_id
    except Exception as e:
        print(f"Failed to get processor ID: {e}")
        return f"Error getting processor ID: {e}"

def get_system_id():
    try:
        processor_id = get_processor_id()
        motherboard_serial = get_motherboard_serial()
        combo = f"{processor_id}:{motherboard_serial}".encode("utf-8")
        systemId = hashlib.blake2b(combo, digest_size=32).hexdigest()[:16]
        return systemId
    except Exception:
        return "Unavailable"

if __name__ == "__main__":
    # system_id = get_system_id()
    # sys_id_file = os.path.join(REPORT_DIR, "sysid.txt")
    # with open(sys_id_file, "w") as f:
    #     f.write(system_id)
    print(get_system_id())
