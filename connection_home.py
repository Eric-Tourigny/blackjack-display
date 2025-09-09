import time
import network
ssid = "SHAW-5AA1E0"
password = '25117C082294'

def connect():
    # Connect to WLAN
    # Connect function from https://projects.raspberrypi.org/en/projects/get-started-pico-w/2
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password) # Remove password if using airuc-guest
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
        
        
try:
    connect()
except KeyboardInterrupt:
    machine.reset()

print('Connected.')
