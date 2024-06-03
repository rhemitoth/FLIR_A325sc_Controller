#### Import libraries ####
import telnetlib # for establishing telnet connection to focus camera
import datetime # for creating image filenames with datetime of image capture
import PySpin # FLIR spinnaker SDK
from gpiozero import LED # for controlling indicator light
from gpiozero import MotionSensor # for controlling motion trigger
from gpiozero import Button # for controlling button to focus camera
from time import sleep # for pausing code
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


#### Establishing Telnet Connection ####
def establish_telnet_connection(cam_ip):
	telnet_connection = telnetlib.Telnet(cam_ip)
	return telnet_connection

#### Focusing the camera via telnet ####
def focus(telnet_connection):
	telnet_connection.read_until(b'>')
	telnet_connection.write(b'rset .system.focus.autofull true\n') # telnet command to focus the camera
	time.sleep(5)

#### Main Code ####

def main():

	# Define LED and PIR sensor GPIO pins on Raspberry Pi
	led = LED(15) # comment this line out if you aren't using an indicator light
	pir = MotionSensor(14)
	button = Button(18)

	# Main code
	while True:

		# Focus camera if button is pressed
		if button.is_pressed:
			# Establish telnet connection and focus the camera
			flir_ip = '169.254.0.2' 
			tn = establish_telnet_connection(flir_ip)
			focus(tn)

		# Check if motion is detected
		motion = pir.motion_detected
		
		if motion == True:

			# Turn on indicator light if motion is detected
			led.on()

			# Connect to camera using Spinnaker SDK and save an image if motion is detected
			fpath = "C:/Users/user/Documents/FLIR/Python/pics/"
			#fpath = "pics/"
			save_image_spinnaker(directory = fpath, filetype = "tiff")

			# Set time delay
			time.sleep(15)

		if motion == False:
			# Turn of indicator light if no motion is detected
			led.off()

if __name__ == '__main__':
	main()


