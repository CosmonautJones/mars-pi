"""
Thread-safe MJPEG frame buffer for the Pi Camera 3 (picamera2 / libcamera).

CameraStream starts the camera in a background thread and keeps the latest
JPEG frame available via `get_frame()`.  The Flask server reads from this
buffer and pushes frames down to every connected browser client.
"""

import io
import threading
import time
import logging

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import camera.config as cfg

log = logging.getLogger(__name__)


class _FrameBuffer(io.BufferedIOBase):
    """Write-only IO object that stores the most-recent JPEG frame."""

    def __init__(self):
        self.frame: bytes | None = None
        self.condition = threading.Condition()

    def write(self, buf: bytes) -> int:
        with self.condition:
            self.frame = bytes(buf)
            self.condition.notify_all()
        return len(buf)


class CameraStream:
    """
    Manages a single Picamera2 instance.

    Usage:
        stream = CameraStream()
        stream.start()
        frame = stream.get_frame()   # latest JPEG bytes
        stream.snapshot()            # high-res JPEG bytes
        stream.stop()
    """

    def __init__(self):
        self._buffer = _FrameBuffer()
        self._cam: Picamera2 | None = None
        self._running = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        if self._running:
            return

        self._cam = Picamera2()

        # Low-resolution video config for the MJPEG stream
        video_cfg = self._cam.create_video_configuration(
            main={"size": (cfg.STREAM_WIDTH, cfg.STREAM_HEIGHT)},
            controls={"FrameRate": cfg.STREAM_FPS},
        )
        self._cam.configure(video_cfg)

        # Enable continuous autofocus (Pi Camera Module 3 only)
        try:
            self._cam.set_controls({"AfMode": getattr(
                self._cam.controls, cfg.AUTOFOCUS_MODE, 2
            )})
        except Exception:
            log.warning("Autofocus control not available on this camera.")

        encoder = MJPEGEncoder()
        encoder.quality = cfg.STREAM_QUALITY
        self._cam.start_recording(encoder, FileOutput(self._buffer))
        self._running = True
        log.info(
            "Camera started - %dx%d @ %d fps",
            cfg.STREAM_WIDTH, cfg.STREAM_HEIGHT, cfg.STREAM_FPS,
        )

    def stop(self):
        if self._cam and self._running:
            self._cam.stop_recording()
            self._cam.close()
            self._running = False
            log.info("Camera stopped.")

    # ------------------------------------------------------------------
    # Frame access
    # ------------------------------------------------------------------

    def get_frame(self, timeout: float = 5.0) -> bytes:
        """Block until a new frame is available, then return it."""
        with self._buffer.condition:
            if not self._buffer.condition.wait(timeout=timeout):
                raise TimeoutError("Camera frame timeout - is the camera connected?")
            return self._buffer.frame

    def snapshot(self) -> bytes:
        """
        Capture a single high-resolution JPEG without interrupting the stream.
        Uses a separate Picamera2 instance so the stream keeps running.
        """
        cam = Picamera2()
        still_cfg = cam.create_still_configuration(
            main={"size": (cfg.SNAPSHOT_WIDTH, cfg.SNAPSHOT_HEIGHT)}
        )
        cam.configure(still_cfg)
        cam.start()
        time.sleep(0.5)  # brief warm-up for AE/AWB to settle

        buf = io.BytesIO()
        cam.capture_file(buf, format="jpeg")
        cam.close()
        return buf.getvalue()

    @property
    def is_running(self) -> bool:
        return self._running


# Module-level singleton — imported by server.py
camera_stream = CameraStream()

