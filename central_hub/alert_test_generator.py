"""
alert_test_generator.py

A simple Python script to simulate IoT sensor alerts by publishing MQTT messages to your central hub.

Usage:
  python alert_test_generator.py \
    --host 192.168.0.100 \
    --port 1883 \
    --nodes esp01 esp02 \
    --sensors pir doppler \
    --interval 5 \
    --count 10

This will publish 10 alert messages at 5‑second intervals to topics like home/sensor/esp01/pir.
"""

import argparse
import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt


def main():
    parser = argparse.ArgumentParser(
        description="Simulate IoT sensor alerts by publishing MQTT messages to the central hub."
    )
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="localhost",
        help="MQTT broker hostname or IP"
    )
    parser.add_argument(
        "--port", "-P",
        type=int,
        default=1883,
        help="MQTT broker port"
    )
    parser.add_argument(
        "--nodes", "-n",
        nargs="+",
        default=["esp01"],
        help="List of node IDs to simulate"
    )
    parser.add_argument(
        "--sensors", "-s",
        nargs="+",
        default=["pir"],
        help="List of sensor types (e.g. pir, doppler)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=30.0,
        help="Seconds between messages"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=0,
        help="Number of messages to send (0 for infinite)"
    )
    args = parser.parse_args()

    # Create MQTT client
    client = mqtt.Client()
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()


    # sleep for a bit to ensure connection
    time.sleep(10)
    sent = 0
    try:
        while True:
            # Pick random node and sensor
            node = random.choice(args.nodes)
            sensor = random.choice(args.sensors)
            # Build payload
            payload = {
                "node": node,
                "sensor": sensor,
                "ts": datetime.now().isoformat()
            }
            topic = f"home/sensor/{node}/{sensor}"
            client.publish(topic, json.dumps(payload))
            print(f"[{datetime.now().isoformat()}] Published to {topic}: {payload}")

            sent += 1
            if args.count and sent >= args.count:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nInterrupted by user, shutting down.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
