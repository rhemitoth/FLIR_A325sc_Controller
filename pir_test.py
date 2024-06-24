# modules
from gpiozero import MotionSensor
from time import sleep

# set pir
pir = MotionSensor(20)

while True:
	motion =  pir.motion_detected
	if motion == True:
		print("motion detected")
	else:
		print("no motion detected")
	sleep(1)