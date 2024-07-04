import subprocess

def is_sd_card_connected():
    def list_block_devices():
        # Execute lsblk command to list block devices
        result = subprocess.run(['lsblk', '-o', 'NAME,TYPE'], capture_output=True, text=True)
        return result.stdout

    def find_sd_card(devices_info):
        # Parse the output of lsblk to find the SD card
        lines = devices_info.strip().split('\n')
        for line in lines:
            if 'sd' in line:  # Typically, SD cards will be named /dev/sdX where X is a letter
                parts = line.split()
                device_name = parts[0]
                device_type = parts[1]
                
                if device_type == 'disk':
                    return True
        return False

    devices_info = list_block_devices()
    return find_sd_card(devices_info)

# Example usage:
if __name__ == "__main__":
    if is_sd_card_connected():
        print("SD card is connected.")
    else:
        print("No SD card connected.")
