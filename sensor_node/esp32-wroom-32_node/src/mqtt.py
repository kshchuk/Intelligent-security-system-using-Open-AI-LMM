import time
import ubinascii
import machine
import ujson as json

from umqtt.robust import MQTTClient   # auto‐reconnect
from network import WLAN              # for isconnected()

import wifi_manager
import blinker

class MQTTManager:
    def __init__(self,
                 broker: str,
                 port: int = 1883,
                 user: str = None,
                 password: str = None,
                 topic_prefix: str = "home/sensor/",
                 keepalive: int = 60):
        # Unique client ID based on MAC
        client_id = ubinascii.hexlify(machine.unique_id())
        self.client = MQTTClient(client_id,
                                 broker,
                                 port=port,
                                 user=user,
                                 password=password,
                                 keepalive=keepalive)
        self.topic_prefix = topic_prefix.encode()
        # last‐will to signal ungraceful disconnect
        self.client.set_last_will(self.topic_prefix + b"status",
                                  b'{"status":"offline"}',
                                  retain=True)

    def connect(self):
        """Connect to the broker and announce online status."""
        print("[MQTT] Connecting to broker…")
        self.client.connect()
        print("[MQTT] Connected to broker.")

        # Publish an “online” status message with retain
        self.client.publish(self.topic_prefix + b"status",
                            b'{"status":"online"}',
                            retain=True)
        print("[MQTT] Connected and online.")

    def publish(self, node: str, sensor: str, payload: dict):
        """Publish a JSON payload under topic_prefix/node/sensor."""
        topic = b"%s%s/%s" % (self.topic_prefix,
                              node.encode(),
                              sensor.encode())
        msg = json.dumps(payload).encode()
        try:
            self.client.publish(topic, msg)
            print(f"[MQTT] Published to {topic}: {msg}")
        except OSError as e:
            print("[MQTT] Publish error:", e)
            self.reconnect()

    def check(self):
        """Call periodically to service network and auto‐reconnect."""
        try:
            # in umqtt.robust this is a no-op unless subscribed
            self.client.ping()
        except OSError:
            self.reconnect()

    def reconnect(self):
        """Attempt to reconnect until success."""
        print("[MQTT] Reconnecting…")
        # wait a bit in case Wi-Fi dropped

        t = blinker.start_blink(200)

        wifi = wifi_manager.WiFiManager(ap_ssid="ESP32-AP", ap_password="12345678", authmode=3, profile_file='wifi.dat', port=80)
        wifi.run() # This will block until Wi-Fi is connected

        blinker.stop_blink(t)

        while not WLAN(WLAN.IF_STA).isconnected():
            print(".", end="")
            time.sleep(1)
        time.sleep(1)
        try:
            self.connect()
        except OSError as e:
            print("[MQTT] Reconnect failed:", e)
            time.sleep(5)
            self.reconnect()