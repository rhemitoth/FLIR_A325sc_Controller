#### Import  Modules ####

#Modules for establishing telnet connection between FLIR and pi
import telnetlib # for establishing telnet connection to focus camera

# Modules for working with GPIO input
from gpiozero import MotionSensor # for reading PIR input
import gpiozero # for controlling relay

# Modules for capturing and saving images with the FLIR
import datetime # for creating image filenames with datetime of image capture
import PySpin # FLIR spinnaker SDK

# Modules for controlling the e-paper display
import os # for checking if directory for image export exists (avoids errors while swapping SD cards) and working with the e-ink display
import sys 
from waveshare_epd import epd2in7_V2 # Using the 2.7 inch Waveshare e-paper HAT
from PIL import Image,ImageDraw,ImageFont

# Other modules
from time import sleep # for pausing code
import time

#### Connect to Camera and Grab Image ####
# Function uses the PySpin library/FLIR Spinnaker SDK
# to connect to the camera and grab an image

def save_image_spinnaker(directory, filetype, burst = True, burst_num = 3):
    # Argument 'directory' specifies directory where image will be saved
    # Argument 'filetype' specifies filetype of image to be saves ('png', 'jpg', 'tiff', etc)
    
    # Initalize the system
    system = PySpin.System.GetInstance()

    # Get the camera
    cam = system.GetCameras()[0]
    
    try:
        if burst == False:
            # Initialize the camera
            cam.Init()

            # Start aquisition
            cam.BeginAcquisition()

            # Grab image
            image_result = cam.GetNextImage()
        
            # Save image
            filename = directory + 'file-' + str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')) + "." + filetype
            if os.path.exists(directory):
                image_result.Save(filename)

            # Release image
            image_result.Release()

            # Stop Acquisition
            cam.EndAcquisition()

            # Deinitalize camera
            cam.DeInit()
        else:
            # Initialize the camera
            cam.Init()

            # Start aquisition
            cam.BeginAcquisition()

            for i in range(0,burst_num):

                # Grab image
                image_result = cam.GetNextImage()
        
                # Save image
                filename = directory + "file-" + str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')) +  "_burst" + str(i+1) + "." + filetype
                if os.path.exists(directory):
                    image_result.Save(filename)

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

#### Drawing an image on the e-ink display ####

def print_to_display(deer_on = True, deer_path = "/home/moorcroftlab/Documents/FLIR/FLIR_A325sc_Controller/raspi_text_background_wlogo.bmp", message = "hello deer",textX = 20,textY = 60,fontPath = "/usr/share/fonts/X11/Type1/NimbusMonoPS-Bold.pfb",fontSize = 18):
    # This function is used to print out messages describing what the system is doing to the e-paper display
    # deer_on = True, the messages will appear as text inside of a speech bubble coming from a cartoon of a roe deer (I'm using this system to capture images of roe deer and I thought it would be cute ¯\_(ツ)_/¯)
    # deer_on = False, the message will appear as plain text 
    # deer_path = location on your Pi where the deer image is saved
    # message = "the text you want to display on the screen"
    # textX = X position to draw text
    # textY = Y position to draw text
    # fontPath = Path to the font you want to use. You can get a list of paths of fonts installed on your Pi by typing "fc-list" in the terminal

    if deer_on == True:
        epd = epd2in7_V2.EPD()
        epd.init()
        epd.Clear()
        
        #Create a blank image for drawing
        canvas = Image.new('1',(epd.width,epd.height),255)
        draw = ImageDraw.Draw(canvas)

        # Load the bitmap image
        image_path = deer_path
        bmp_image = Image.open(image_path)
        bw_image = bmp_image.convert('1')
        bmp_width,bmp_height = bw_image.size

        # Position to paste the bitmap image
        x_offset = 0
        y_offset = 0

        # Paste the bitmap image onto the canvas
        canvas.paste(bw_image,(x_offset,y_offset))

        # Load a font
        font_path = fontPath
        txt_font = ImageFont.truetype(font_path,fontSize)

        # Define the text to display
        text = message

        # Position to draw the text
        text_x = textX
        text_y = textY

        # Draw the text on the canvas
        draw.text((text_x, text_y),text,font=txt_font,fill=0)

        # Display the image on the e-Paper display
        epd.display_Fast(epd.getbuffer(canvas))
    else:
        epd = epd2in7_V2.EPD()
        epd.init()
        epd.Clear()
        
        #Create a blank image for drawing
        canvas = Image.new('1',(epd.width,epd.height),255)
        draw = ImageDraw.Draw(canvas)
        
        # Load a font
        font_path = fontPath
        txt_font = ImageFont.truetype(font_path,fontSize)
    
        # Define the text to display
        text = message
        
        # Position to draw the text
        text_x = textX
        text_y = textY
        
        # Draw the text on the canvas
        draw.text((text_x, text_y),text,font=txt_font,fill=0)
        
        # Display the image on the e-Paper display
        epd.display_Fast(epd.getbuffer(canvas))

#### Clear the e-ink display #####
def clear_display():
    epd = epd2in7_V2.EPD()
    epd.init()
    epd.Clear()

#### Save pictures #####
def collect_data(fpath = "/media/moorcroftlab/9016-4EF8/",duration = 5, frequency = 5):
    # f_path = "directory where images will be saved"
    # duration = duration in minutes of data collection
    # frequency = frequency at which image bursts are captured
    start_time = time.time()
    elapsed_time = 0
    check_sd_count = 0
    image_capture_count = 0
    while elapsed_time < duration * 60:
        if os.path.exists(fpath) == False:
            print("WARNING: SD Card missing.")
            if check_sd_count == 0:
                print_to_display(message = "WARNING.\nNo SD card \ndetected.")
            check_sd_count += 1
            sd_missing = True
            while sd_missing == True:
                sd_missing = os.path.exists(fpath)
                sleep(1)
        elif os.path.exists(fpath) and check_connection() == True:
            if image_capture_count == 0:
                print_to_display(message = "Capturing \nimages.")
            print("Capturing image . . .")
            save_image_spinnaker(directory = fpath, filetype = "tiff")
            print ("Image saved.")
            sleep(frequency)
            image_capture_count += 1
        elapsed_time = time.time() - start_time
         
#### Main Code ####

def main():

    # Define PIR sensor GPIO pins on Raspberry Pi
    pir = MotionSensor(20)
    relay = gpiozero.OutputDevice(21, active_high = True, initial_value = False)

    # Main code 

    count = 0 # used to check if while loop is on first iteration
    
    while True: 
        # Check if motion is detected
        previous_motion = False
        current_motion = pir.motion_detected
        
        if current_motion == True and previous_motion == False:

            # Turn on camera
            print("Motion detected. Turning on camera")
            relay.on()
            
            # Pause code until camera is connected
            print("Connecting to camera . . .")
            print_to_display(message = "Connecting\nto camera.")
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
                        print_to_display(message = "No cam\ndetected.\nRestarting\nsystem.", fontSize = 16)
                        relay.off()
                        sleep(60)
                        relay.on()
                        print("Connecting to camera . . .")
                        print_to_display(message = "Connecting\nto camera.")
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
                print_to_display(message = "Focusing\ncamera.")
                focus(tn)
                print("Camera is focused.")

            # Collect and image every 10 seconds for 30 minutes
            collect_data(duration = 1)
            
            # Update global count variable
            count = 0


        if current_motion == False:
            relay.off() # turn off relay/power off camera
            print("No motion detected. Camera off.")
            if count == 0:
                print_to_display(message = "No motion\ndetected.\nCamera off.")
            sleep(1) # prevents the camera from freezing from turning on/off to quickly
            previous_motion = False
            # This prevents the display from constantly refreshing when there is no motion
            count +=1
            if count == 2:
                count -= 1
            
if __name__ == '__main__':
    main()




