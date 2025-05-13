from machine import Pin
from time import sleep

from mqtt import MQTTManager

import network

led = Pin(2, Pin.OUT)

def main():
  # wifi is already connected by the boot.py

  mqtt_manager = MQTTManager(
      broker="192.168.0.107",
      port=1883,
      user="user",
      password="password",
      topic_prefix="home/sensor/",
      keepalive=60
  )

  mqtt_manager.connect()

  while True:
    led.value(not led.value())
    mqtt_manager.publish(
        node="esp32",
        sensor="led",
        payload={"state": "on" if led.value() else "off"}
    )
    sleep(0.5)

if __name__ == "__main__":
    main()