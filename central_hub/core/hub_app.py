import asyncio
import threading
import time

import cv2
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import requests
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket
from starlette.status import WS_1008_POLICY_VIOLATION

from envs import (
    IMAGE_DIR,
    CAMERA_INDEX,
    CONFIG_SYNC_INTERVAL,
    CENTRAL_API_URL,
    HUB_NAME,
    SECRET_KEY,
    ALGORITHM,
)


class HubApp:
    """
    Encapsulates the FastAPI application, routes, and streaming.
    """
    def __init__(self):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.state.websockets = []
        self.app.state.sensor_flags: dict[str, bool] = {}

        self.hub_id = None

        # Mount static folders
        self.app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")
        # Setup routes
        self._setup_routes()

        # Register hub and fetch initial configuration (nodes/sensors)
        self._register_from_central()
        try:
            self._sync_config_from_central()
        except Exception as e:
            print(f"[SYNC] Initial config sync failed: {e}")
        # Start periodic config sync
        threading.Thread(target=self._config_sync_loop, daemon=True).start()

    def _setup_routes(self):
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{CENTRAL_API_URL}/auth/token")

        async def _get_current_user(token: str = Depends(oauth2_scheme)):
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                if username is None:
                    raise credentials_exception
            except JWTError:
                raise credentials_exception
            return username

        @self.app.get("/alerts", dependencies=[Depends(_get_current_user)])
        def get_alerts():
            return self.app.state.store.get_alerts()

        @self.app.websocket("/ws/alerts")
        async def ws_alerts(ws: WebSocket, token: str = Depends(oauth2_scheme)):
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                if username is None:
                    raise JWTError()
            except JWTError:
                await ws.close(code=WS_1008_POLICY_VIOLATION)
                return
            await ws.accept()
            self.app.state.websockets.append(ws)
            try:
                while True:
                    await asyncio.sleep(1)
            finally:
                self.app.state.websockets.remove(ws)

        @self.app.get(
            "/stream/video.mjpg",
            dependencies=[Depends(_get_current_user)],
            responses={200: {"content": {"multipart/x-mixed-replace; boundary=frame": {}}}},
            response_class=StreamingResponse,
        )
        def stream_video_mjpg():
            return StreamingResponse(
                self._mjpeg_stream(),
                media_type="multipart/x-mixed-replace; boundary=frame",
            )

    def _mjpeg_stream(self):
        cap = cv2.VideoCapture(CAMERA_INDEX)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, jpeg = cv2.imencode(".jpg", frame)
            yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
            )

    def _config_sync_loop(self):
        while True:
            try:
                self._sync_config_from_central()
            except Exception as e:
                print(f"[SYNC] Error syncing config: {e}")
            time.sleep(CONFIG_SYNC_INTERVAL)

    def _register_from_central(self):
        """
        PUT /hub/register with ip address and name
        """
        url = f"{CENTRAL_API_URL}/hub/register"
        ip = requests.get("https://api.ipify.org").text
        name = HUB_NAME
        data = {
            "ip": ip,
            "name": name,
        }
        resp = requests.put(url, json=data)
        resp.raise_for_status()
        result = resp.json()
        self.hub_id = result.get("hub_id")
        # expose hub_id to other components (e.g. MQTT handler)
        self.app.state.hub_id = self.hub_id
        print(f"[SYNC] Registered with central server: {result}")

    def _sync_config_from_central(self):
        """
        Fetch /hub/{HUB_ID}/config -> sensors, update sensor_flags.

        sensor_flags - mean "enabled" or "disabled" for each sensor.
        if enabled, process the alert.
        if disabled, skip the alert.

        """
        url = f"{CENTRAL_API_URL}/hub/{self.hub_id}/config"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        # build sensor flag map
        new_flags: dict[str, bool] = {}
        # cache of known nodes and sensors for auto-registration
        known_nodes: set[str] = set()
        node_id_map: dict[str, int] = {}
        known_sensors: dict[str, set[str]] = {}
        for node in data.get("nodes", []):
            node_key = node.get('location')
            node_id = node.get('id')
            known_nodes.add(node_key)
            node_id_map[node_key] = node_id
            sensors = set()
            for sensor in node.get('sensors', []):
                sensor_key = sensor.get('type')
                enabled = sensor.get('status', '') == 'enabled'
                new_flags[f"{node_key}/{sensor_key}"] = enabled
                sensors.add(sensor_key)
            known_sensors[node_key] = sensors
        self.app.state.sensor_flags = new_flags
        self.app.state.known_nodes = known_nodes
        self.app.state.node_id_map = node_id_map
        self.app.state.known_sensors = known_sensors
        print(f"[SYNC] Updated sensor flags: {new_flags}")

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000)