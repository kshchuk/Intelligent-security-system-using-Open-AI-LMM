from machine import Pin
import time

import network
import mqtt
from hw416 import HW416

led = Pin(2, Pin.OUT)

# wifi is already connected by the boot.py
mqtt_manager = mqtt.MQTTManager(
      broker="192.168.0.107",
      port=1883,
      user="user",
      password="password",
      topic_prefix="home/sensor/",
      keepalive=60
)

mqtt_manager.connect()


def on_motion(state: bool):
    led.value(state)

    payload = {
        "sensor": "HW-416",
        "motion": state,
        "ts": time.time()
    }
    mqtt_manager.publish("esp01", "pir", payload)

hw = HW416(pin_no=14, callback=on_motion, debounce_ms=300)

def main():

  while True:
    # led.value(not led.value())
    time.sleep(0.5)

if __name__ == "__main__":
    main()