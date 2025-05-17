import asyncio

import cv2
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from envs import IMAGE_DIR, CAMERA_INDEX


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

        # Mount static folders
        self.app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/alerts")
        def get_alerts():
            return self.app.state.store.get_alerts()

        @self.app.websocket("/ws/alerts")
        async def ws_alerts(ws: WebSocket):
            await ws.accept()
            self.app.state.websockets.append(ws)
            try:
                while True:
                    await asyncio.sleep(1)
            finally:
                self.app.state.websockets.remove(ws)

        @self.app.get("/stream/video.mjpg",
                 responses={200: {"content": {"multipart/x-mixed-replace; boundary=frame": {}}}},
                 response_class=StreamingResponse)
        def stream_video_mjpg():
            return StreamingResponse(
                self._mjpeg_stream(),
                media_type="multipart/x-mixed-replace; boundary=frame"
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

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000)