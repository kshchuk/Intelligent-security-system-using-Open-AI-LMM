import os

DB_PATH = "alerts/alertdb.sqlite"
CAMERA_INDEX = 0
IMAGE_DIR = "images"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

CENTRAL_API_URL = os.getenv("CENTRAL_API_URL", "http://localhost:8001")
HUB_ID = int(os.getenv("HUB_ID", "0"))
CONFIG_SYNC_INTERVAL = int(os.getenv("CONFIG_SYNC_INTERVAL", "10"))