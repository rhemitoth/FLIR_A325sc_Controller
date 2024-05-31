# Import libs
import telnetlib
import ftplib
import datetime
import time
import PySpin

# Connect to camera
flir_ip = '169.254.0.1'
tn = telnetlib.Telnet(flir_ip)

#Focus the camera
tn.read_until(b'>')
tn.write(b'rset .system.focus.autofull true\n')
time.sleep(5)

