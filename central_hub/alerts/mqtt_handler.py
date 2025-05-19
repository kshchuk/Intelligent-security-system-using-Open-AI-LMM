import asyncio
import json
import threading
from datetime import datetime

from paho.mqtt.client import Client as MQTTClient

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

        # Check flag
        key = f"{node}/{sensor}"
        if not self.app.state.sensor_flags.get(key, True):
            print(f"[MQTT] Skipping alert for disabled sensor {key}")
            return

        # Only process if motion==True
        if not payload.get("motion", False):
            return

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