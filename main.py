from exploit.restore import restore_files, FileToRestore
from pymobiledevice3.lockdown import create_using_usbmux
import re
import sys
import os
import subprocess
import json

def detect_device():
    try:
        lockdown = create_using_usbmux()
    except Exception as e:
        return None

    info = lockdown.all_values
    return {
        "client": lockdown,
        "name": info.get("DeviceName", "Unknown Device"),
        "version": info.get("ProductVersion", "Unknown"),
    }

def is_supported_ios(version_str: str) -> bool:
    match = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?(?:b(\d+))?", version_str)
    if not match:
        return False

    major, minor, patch, beta = match.groups()
    major = int(major)
    minor = int(minor)

    if major < 18:
        return True
    if major == 18 and minor < 1:
        return True

    return False

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    global device

    print("WARNING: Modifying system files incorrectly and without knowing what you are doing can cause issues to iOS or fully break it and may require a full restore of your device in severe cases.")
    print("Use at your own risk.")
    agree = input("Type Y to agree and continue: ").strip().upper()

    if agree != "Y":
        print("Aborting.")
        sys.exit(0)

    cls()

    device = detect_device()

    if not device:
        print("No device detected. Please connect a device and try again.")
        sys.exit(1)

    print(f"Connected to {device['name']} running iOS {device['version']}.")

    if not is_supported_ios(device['version']):
        print("\n May have detected an unsupported version of iOS 18.1 or newer.")
        print("SparseRestore was fixed in iOS 18.1 beta 6 and newer.")
        print("If you are on iOS 18.1 beta 1-5 then you can safely ignore this message.")

    local_file = input("\nDrag and drop your file here: ").strip().strip('"')

    try:
        with open(local_file, "rb") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Unable to read file: {e}")
        sys.exit(1)

    directory_path = input("Enter the exact directory path you want the file to be restored to on the device (e.g /private/var): ").strip()
    file_name = input("Enter the file name to restore as (e.g example.jpg): ").strip()

    try:
        restore_files(
            files=[FileToRestore(
                contents=file_content,
                restore_path=directory_path,
                restore_name=file_name
            )],
            reboot=False,
            lockdown_client=device["client"]
        )

        print(f"\nSuccessfully restored '{file_name}' to {directory_path}")

    except Exception as e:
        print(f"\nRestore failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
