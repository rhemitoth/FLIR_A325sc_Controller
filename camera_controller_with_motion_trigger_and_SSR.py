#### Import libraries ####
import telnetlib # for establishing telnet connection to focus camera
import datetime # for creating image filenames with datetime of image capture
import PySpin # FLIR spinnaker SDK
from gpiozero import LED # for controlling indicator light
from gpiozero import MotionSensor # for controlling motion trigger
from gpiozero import Button # for controlling button to focus camera
import gpiozero # for controlling relay
from time import sleep # for pausing code
from time import time
import os # for checking if directory for image export exists (avoids errors while swapping SD cards)


#### Connect to Camera and Grab Image ####
# Function uses the PySpin library/FLIR Spinnaker SDK
# to connect to the camera and grab an image

def save_image_spinnaker(directory, filetype):
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
		filename = directory + 'file-' + str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')) + "." + filetype
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

#### Main Code ####

def main():

	# Define LED and PIR sensor GPIO pins on Raspberry Pi
	led = LED(23) # comment this line out if you aren't using an indicator light
	pir = MotionSensor(24)
	relay = gpiozero.OutputDevice(21, active_high = True, initial_value = False)


	# Main code 
	
	# Initialize previous  motion state
	previous_motion = False
	
	while True:
		# Check if motion is detected
		
		current_motion = pir.motion_detected
		
		if previous_motion == True and current_motion == False:
			sleep(10) # prevents camera from freezing up from turning off/on too quickly
		
		if current_motion == True:

			# Turn on indicator light if motion is detected
			led.on()

			# Turn on camera
			print("Motion detected. Turning on camera")
			relay.on()
			
			# Pause code until camera is connected
			print("Connecting to camera . . .")
			not_connected = True
			start_time = time()
			while not_connected == True:
				connection_status = check_connection()
				if connection_status == True:
					not_connected = False
				else:
					current_time = time()
					if current_time - start_time > 60:
						print("Camera frozen. Restarting . . . ")
						relay.off()
						sleep(60)
						relay.on()
						print("Connecting to camera . . .")
						sleep(1)
						start_time = time()
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

			# while motion is still detected, collect an image every 10 seconds
			still_moving = current_motion
			while still_moving == True:
				fpath = "/media/moorcroftlab/9016-4EF8/"
				if os.path.exists(fpath) and check_connection() == True:
					print("Capturing image . . .")
					save_image_spinnaker(directory = fpath, filetype = "tiff")
					print ("Image saved.")
					# blink LED after saving an image
					led.off()
					sleep(1)
					led.on()
					# wait 5 seconds before taking the next picture
					sleep(5)
				elif os.path.exists(fpath) == False:
					print("WARNING: SD Card missing.")
					sleep(1)

				# check to see if motion is still detected before taking another picture
				# Exit while loop if motion is no longer detected
				still_moving = pir.motion_detected

		if current_motion == False:
			# Turn of indicator light if no motion is detected
			led.off()
			sleep(1)
			
			# Turn relay off
			relay.off()
			print("No motion detected. Camera off.")
			sleep(2)
		
		previous_motion = current_motion
			
			
			
if __name__ == '__main__':
	main()


