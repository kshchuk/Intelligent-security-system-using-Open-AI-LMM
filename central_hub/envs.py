import os

DB_PATH = "alerts/alertdb.sqlite"
CAMERA_INDEX = 0
IMAGE_DIR = "images"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

CENTRAL_API_URL = os.getenv("CENTRAL_API_URL", "http://localhost:8001")
HUB_NAME = str(os.getenv("HUB_NAME", "HUB_NAME"))
CONFIG_SYNC_INTERVAL = int(os.getenv("CONFIG_SYNC_INTERVAL", "10"))
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
ALGORITHM = "HS256"