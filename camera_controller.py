#### Import libraries ####
import telnetlib
import ftplib
import datetime
import time
import PySpin

#### Connect to camera ####
def establish_telnet_connection(cam_ip):
	telnet_connection = telnetlib.Telnet(cam_ip)
	return telnet_connection

#### Focus the camera ####
def focus(telnet_connection):
	telnet_connection.read_until(b'>')
	telnet_connection.write(b'rset .system.focus.autofull true\n') # telnet command to focus the camera
	time.sleep(5)

def main():
	flir_ip = '169.254.0.2' # Camera IP address
	tn = establish_telnet_connection(flir_ip)
	focus(tn)

if __name__ == '__main__':
	main()


