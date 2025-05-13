from time import sleep

from wifi_manager import WiFiManager
import blinker

# Blinking is a signal that the device is connecting to the network.
t = blinker.start_blink(200)

# Searches in local storage for a wifi credentials, if not found - exposes web server on 192.168.4.1
wifi = WiFiManager(ap_ssid="ESP32-AP", ap_password="12345678", authmode=3, profile_file='wifi.dat', port=80)
wifi.run()

blinker.stop_blink(t)

