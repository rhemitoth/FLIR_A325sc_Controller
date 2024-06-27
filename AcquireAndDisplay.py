#### Import  Modules ####

#Modules for establishing telnet connection between FLIR and pi
import telnetlib # for establishing telnet connection to focus camera

# Modules for capturing and saving images with the FLIR
import datetime # for creating image filenames with datetime of image capture
import PySpin # FLIR spinnaker SDK

# Other modules
import matplotlib
from PIL import Image,ImageDraw,ImageFont
import time
from time import sleep
import matplotlib.image as mpimg

#### Connect to Camera and Grab Image ####
# Function uses the PySpin library/FLIR Spinnaker SDK
# to connect to the camera and grab an image

def display_image(pause = 5):
    # Argument 'directory' specifies directory where image will be saved
    # Argument 'filetype' specifies filetype of image to be saves ('png', 'jpg', 'tiff', etc)
    
    # Initalize the system
    system = PySpin.System.GetInstance()

    # Get the camera
    cam = system.GetCameras()[0]
    
    try:
        # Initialize the camera
        cam.Init()

        # Start aquisition
        cam.BeginAcquisition()

        # Grab image
        image_result = cam.GetNextImage()

        # Save image
        image_result.Save("temp.tiff")


        img=mpimg.imread('temp.TIF ')
        imgplot = plt.imshow(img)

        # Pause
        sleep(pause)

        # Close plot
        plt.close('all')

        # Release image
        image_result.Release()

        # Stop Acquisition
        cam.EndAcquisition()

        # Deinitalize camera
        cam.DeInit()

    finally:
        # Release system instance
        system.ReleaseInstance()


#### Check for camera connection ####
# Function generates a list of connected cameras using the FLIR spinnaker SDK 
# Returns 'False' if no cameras are connected
# Returns 'True' if a camera is connected

def check_connection():
    # Initalize the system
    system = PySpin.System.GetInstance()

    # Get the list of connected cameras
    cam_list = system.GetCameras()

    # Get length of camera list
    numcams = len(cam_list)

    # Return true if the camera is connected. Return false is no camera is connected.
    if numcams > 0:
        return True
    else:
        return False

#### Establishing Telnet Connection ####
def establish_telnet_connection(cam_ip):
    telnet_connection = telnetlib.Telnet(cam_ip)
    return telnet_connection

#### Focusing the camera via telnet ####
def focus(telnet_connection):
    telnet_connection.read_until(b'>')
    telnet_connection.write(b'rset .system.focus.autofull true\n') # telnet command to focus the camera
    sleep(5)


#### Main Code ####

def main():

    while True: 
        not_connected = True
        start_time = time.time()
        while not_connected == True:
            connection_status = check_connection()
            if connection_status == True:
                not_connected = False
            else:
                current_time = time.time()
                if current_time - start_time > 60:
                    print("Camera frozen. Restarting . . . ")
                    relay.off()
                    sleep(60)
                    relay.on()
                    print("Connecting to camera . . .")
                    sleep(1)
                    start_time = time.time()
                else:
                    sleep(1)
        print("Camera connected.")

        # Focus the camera
        if check_connection() == True:
            flir_ip = '169.254.0.2' 
            tn = establish_telnet_connection(flir_ip)
            print("Focusing camera . . .")
            focus(tn)
            print("Camera is focused.")

        while check_connection() == True:
            display_image()
            
if __name__ == '__main__':
    main()




