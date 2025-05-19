import os

from core.ai_analyzer import AIAnalyzer
from alerts.alert_db import AlertStore
from core.camera_capture import CameraCapture
from envs import IMAGE_DIR, DB_PATH, CAMERA_INDEX, MQTT_BROKER, MQTT_PORT
from core.hub_app import HubApp
from alerts.mqtt_handler import MQTTHandler

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # Initialize components
    store = AlertStore(DB_PATH)
    camera = CameraCapture(index=CAMERA_INDEX)
    analyzer = AIAnalyzer()
    hub = HubApp()
    # Attach store to FastAPI state for route handlers
    hub.app.state.store = store

    # Start MQTT subscriber
    mqtt_handler = MQTTHandler(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        topic="home/sensor/+/+",
        store=store,
        camera=camera,
        analyzer=analyzer,
        app=hub.app,
    )

    # Launch the API server (includes REST, WS, MJPEG)
    hub.run()