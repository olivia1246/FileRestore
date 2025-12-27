from exploit.restore import restore_files, FileToRestore
import re
import sys

device = None

def is_supported_ios(version_str: str) -> bool:
    match = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?(?:b(\d+))?", version_str)
    if not match:
        return False

    major, minor, patch, beta = match.groups()
    major = int(major)
    minor = int(minor)
    beta = int(beta) if beta else 0

    if major < 18:
        return True
    if major == 18 and minor < 1:
        return True
    if major == 18 and minor == 1:
        return beta <= 5

    return False


def main():
    global device

    print("\nWARNING: Modifying system files incorrectly and without knowing what you are doing can cause issues to iOS or fully break it and may require a full restore of your device in severe cases.")
    print("Use at your own risk.")
    agree = input("Type Y to agree and continue: ").strip().upper()

    if agree != "Y":
        print("Aborting.")
        sys.exit(0)

    if not device:
        print("No device detected. Please connect a device and try again.")
        sys.exit(1)

    print(f"Connected to {device.name} running iOS {device.version}")

    if not is_supported_ios(device.version):
        print("\nDetected an unsupported version of iOS.")
        print("SparseRestore was fixed in iOS 18.1 beta 6 and newer.")
        print("This may not work for your device.")

    local_file = input("\nDrag and drop your file here: ").strip()

    try:
        with open(local_file, "rb") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Unable to read file: {e}")
        sys.exit(1)

    directory_path = input("Enter the exact directory path you want the file to be restored to on the device (e.g /private/var): ").strip()
    file_name = input("Enter the file name you would like to have the restore to use (e.g example.jpg): ").strip()

    try:
        restore_files(
            files=[FileToRestore(
                contents=file_content,
                restore_path=directory_path,
                restore_name=file_name
            )],
            reboot=False,
            lockdown_client=None
        )

        print(f"\nSuccessfully restored '{file_name}' to {directory_path}")

    except Exception as e:
        print(f"\nRestore failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
