import subprocess
import os

def list_block_devices():
    # Execute lsblk command to list block devices
    result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'], capture_output=True, text=True)
    return result.stdout

def find_sd_card(devices_info):
    # Parse the output of lsblk to find the SD card
    lines = devices_info.strip().split('\n')
    for line in lines:
        if 'sd' in line:  # Typically, SD cards will be named /dev/sdX where X is a letter
            parts = line.split()
            device_name = parts[0]
            device_size = parts[1]
            device_type = parts[2]
            mount_point = parts[3] if len(parts) > 3 else None
            
            if device_type == 'disk':
                return device_name, device_size, mount_point
    return None, None, None

def main():
    devices_info = list_block_devices()
    device_name, device_size, mount_point = find_sd_card(devices_info)
    
    if device_name:
        print(f"Found SD card: /dev/{device_name}")
        print(f"Size: {device_size}")
        if mount_point:
            print(f"Mount point: {mount_point}")
        else:
            print("SD card is not mounted.")
    else:
        print("No SD card found.")

if __name__ == "__main__":
    main()
