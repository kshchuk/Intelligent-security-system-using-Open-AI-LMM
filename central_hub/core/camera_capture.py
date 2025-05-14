import os
from datetime import datetime

import cv2

from envs import IMAGE_DIR


class CameraCapture:
    """
    Captures frames from a connected camera.
    """
    def __init__(self, index: int = 0, image_dir: str = IMAGE_DIR):
        self.index = index
        self.image_dir = image_dir
        os.makedirs(self.image_dir, exist_ok=True)

    def capture(self) -> str:
        cam = cv2.VideoCapture(self.index)
        ret, frame = cam.read()
        cam.release()
        if not ret:
            raise RuntimeError("Camera capture failed")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = os.path.join(self.image_dir, f"cap_{ts}.jpg")
        cv2.imwrite(path, frame)
        return path