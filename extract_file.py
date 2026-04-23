import os
from zipfile import ZipFile
import subprocess
from time import *

services = {
        "main.service",
        "logged_data_sync.service",
        "handle_4G.service",
        "system_control.service",
        "ota_manager.service"
    }

PATH = "/home/UbiqCM4"

def control_services(control_command,service):
    """
    The function in which based on control command restart or stop the service
    """
    cmd = f"sudo systemctl {control_command} {service}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    sleep(1)

def copy_to_dest(file, updated_filename):
    source = f"{PATH}/{updated_filename}/{file}"
    dest = f"{PATH}/{file}"
    cmd = f"sudo cp {source} {dest}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

def extract_files(filename):
    """
    Extract files to a specific directory without version number
    """
    # Get base name without extension
    base_name = filename.split('.')[0]

    # Create target directory if it doesn't exist
    if not os.path.exists(base_name):
        os.makedirs(base_name)

    with ZipFile(filename, 'r') as zip_file:
        for zip_info in zip_file.infolist():
            if zip_info.is_dir():
                continue
            zip_info.filename = os.path.basename(zip_info.filename)
            zip_file.extract(zip_info, base_name)

    for service in services:
        control_services('stop', service)
    sleep(1)

    for file in os.listdir(base_name):
        if os.path.isfile(os.path.join(base_name, file)):
            copy_to_dest(file, base_name)

    print("Updating...................")

    for service in services:
        control_services('restart', service)
    sleep(1)

if __name__ == '__main__':
    extract_files(filename="Ub_JTEDS.zip")
