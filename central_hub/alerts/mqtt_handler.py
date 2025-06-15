import asyncio
import json
import threading
from datetime import datetime

from paho.mqtt.client import Client as MQTTClient
import requests
from envs import CENTRAL_API_URL

from alerts.alert_db import AlertStore
from core.ai_analyzer import AIAnalyzer
from core.camera_capture import CameraCapture


class MQTTHandler:
    """
    Subscribes to sensor events over MQTT and triggers processing.
    """
    def __init__(
        self,
        broker: str,
        port: int,
        topic: str,
        store: AlertStore,
        camera: CameraCapture,
        analyzer: AIAnalyzer,
        app,
    ):
        self.store = store
        self.camera = camera
        self.analyzer = analyzer
        self.app = app  # FastAPI instance for websocket notifications

        self.client = MQTTClient()
        self.client.on_message = self._on_message
        self.client.connect(broker, port, keepalive=60)
        self.client.subscribe(topic)

        # Run loop in background thread
        thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        thread.start()

    def _on_message(self, client, userdata, msg):
        topic_parts = msg.topic.split("/")
        node = topic_parts[2]
        sensor = topic_parts[3]
        payload = json.loads(msg.payload.decode())

        # Auto-register new node/sensor in central backend
        hub_id = getattr(self.app.state, "hub_id", None)
        if hub_id is not None:
            # initialize caches if missing
            if not hasattr(self.app.state, "known_nodes"):
                self.app.state.known_nodes = set()
                self.app.state.node_id_map = {}
                self.app.state.known_sensors = {}
            # register node if not yet known
            if node not in self.app.state.known_nodes:
                try:
                    resp_node = requests.post(
                        f"{CENTRAL_API_URL}/hubs/{hub_id}/nodes",
                        json={"location": node},
                    )
                    resp_node.raise_for_status()
                    node_data = resp_node.json()
                    nid = node_data.get("id")
                    self.app.state.known_nodes.add(node)
                    self.app.state.node_id_map[node] = nid
                    self.app.state.known_sensors[node] = set()
                    print(f"[MQTT][AUTO-REG] Created node '{node}' (id={nid})")
                except Exception as e:
                    print(f"[MQTT][AUTO-REG] Failed to create node '{node}': {e}")
            # register sensor if not yet known for this node
            if sensor not in self.app.state.known_sensors.get(node, set()):
                pin_val = payload.get("pin", "")
                try:
                    node_id = self.app.state.node_id_map.get(node)
                    if node_id is None:
                        raise RuntimeError(f"Unknown node id for '{node}'")
                    resp_s = requests.post(
                        f"{CENTRAL_API_URL}/nodes/{node_id}/sensors",
                        json={"type": sensor, "pin": pin_val},
                    )
                    resp_s.raise_for_status()
                    self.app.state.known_sensors[node].add(sensor)
                    print(f"[MQTT][AUTO-REG] Created sensor '{sensor}' on node '{node}'")
                except Exception as e:
                    print(f"[MQTT][AUTO-REG] Failed to create sensor '{sensor}' on node '{node}': {e}")

        # Check flag
        key = f"{node}/{sensor}"
        if not self.app.state.sensor_flags.get(key, True):
            print(f"[MQTT] Skipping alert for disabled sensor {key}")
            return

        # Only process if motion==True
        # if not payload.get("motion", False):
        #    return

        # Capture frame
        image_path = self.camera.capture()
        # Analyze image
        description = self.analyzer.analyze(image_path)
        # Store alert
        self.store.add_alert(node, sensor, image_path, description)
        # Notify websocket clients
        alert = {
            "timestamp": datetime.now().isoformat(),
            "node": node,
            "sensor": sensor,
            "image_path": image_path,
            "description": description,
        }
        # Broadcast to all connected websockets
        for ws in list(self.app.state.websockets):
            asyncio.run(ws.send_text(json.dumps(alert)))