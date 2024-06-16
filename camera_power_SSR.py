# Import libraries

import time
import RPi.GPIO as GPIO

# Set GPIO pin for relay

relay_ch = 21

# Turn on camera using relay

while True:
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(relay_ch, GPIO.OUT)
	GPIO.output(relay_ch, GPIO.LOW)
	GPIO.output(relay_ch, GPIO.HIGH)
	time.sleep(5)
	GPIO.cleanup()

