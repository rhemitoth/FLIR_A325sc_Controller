#### Import libraries ####
import telnetlib
import ftplib
import datetime
import time
import PySpin



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

		# Configure camera settings
		#cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continous)
		#cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
		#cam.ExposureTime.SetValue(10000)

		# Start aquisition
		cam.BeginAcquisition()

		# Grab image
		image_result = cam.GetNextImage()
	
		# Save image
		filename = directory + 'file-' + str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')) + "." + filetype
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

	# Establish telnet connection and focus the camera
	flir_ip = '169.254.0.2' 
	tn = establish_telnet_connection(flir_ip)
	focus(tn)

	# Connect to camera using Spinnaker SDK and save an image
	#fpath = "C:/Users/user/Documents/FLIR/Python/pics/"
	fpath = "pics/"
	save_image_spinnaker(directory = fpath, filetype = "tiff")

if __name__ == '__main__':
	main()


