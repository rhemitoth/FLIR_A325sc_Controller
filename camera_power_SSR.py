# Import libraries

import time
import gpiozero

# Set GPIO pin for relay

relay_ch = 21

# Turn on camera using relay



while True:
    relay = gpiozero.OutputDevice(relay_ch, active_high = True, initial_value = False)
    relay.on()
    print("turned on")
    time.sleep(8)
    relay.off()
    time.sleep(1)
    print("turned off")
    relay.close()
    print("closed relay")
    time.sleep(2)
    
    
