import os
import subprocess

def find_sd_card_mount_point():
    try:
        # Use the 'df' command to list all mounted filesystems
        output = subprocess.check_output(['df', '-h']).decode('utf-8')
        
        # Split the output into lines and iterate over them
        for line in output.splitlines():
            # Check if the line contains '/media' or '/mnt'
            if '/media' in line or '/mnt' in line:
                # Split the line into columns and get the mount point
                columns = line.split()
                mount_point = columns[-1]
                # You can add further checks to identify the SD card specifically
                print(f"Possible SD card mount point: {mount_point}")
                
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        
if __name__ == "__main__":
    find_sd_card_mount_point()
