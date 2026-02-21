"""
mars-pi — grow tent monitoring server
--------------------------------------
Endpoints:
  GET /stream      — MJPEG live stream  (embed as <img src="http://pi:8000/stream">)
  GET /snapshot    — Single high-res JPEG
  GET /health      — JSON status (camera + future sensor fields)
  GET /api/sensors — Placeholder; returns {} until BME280 is wired up
"""

import logging
import signal
import sys
from flask import Flask, Response, jsonify, abort
from flask_cors import CORS

import camera.config as cfg
from camera.stream import camera_stream
from sensors import read_sensors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("mars-pi")

app = Flask(__name__)
CORS(app, origins=cfg.CORS_ORIGINS)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def _mjpeg_generator():
    """Yield MJPEG multipart frames for the /stream endpoint."""
    while True:
        try:
            frame = camera_stream.get_frame()
        except TimeoutError as exc:
            log.error(exc)
            break
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/stream")
def stream():
    """MJPEG live stream — works as an <img> src in any browser."""
    if not camera_stream.is_running:
        abort(503, description="Camera not running.")
    return Response(
        _mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/snapshot")
def snapshot():
    """Return a single high-resolution JPEG capture."""
    if not camera_stream.is_running:
        abort(503, description="Camera not running.")
    try:
        jpeg = camera_stream.snapshot()
    except Exception as exc:
        log.exception("Snapshot failed")
        abort(500, description=str(exc))
    return Response(jpeg, mimetype="image/jpeg")


@app.route("/health")
def health():
    """JSON health/status endpoint — safe to poll from the website."""
    return jsonify({
        "status": "ok",
        "camera": {
            "running": camera_stream.is_running,
            "resolution": f"{cfg.STREAM_WIDTH}x{cfg.STREAM_HEIGHT}",
            "fps": cfg.STREAM_FPS,
        },
        # sensor field will be populated once BME280 is attached
        "sensors": read_sensors(),
    })


@app.route("/api/sensors")
def sensors():
    """Sensor data endpoint — returns empty dict until BME280 is wired up."""
    return jsonify(read_sensors())


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

def _shutdown(sig, frame):
    log.info("Shutting down…")
    camera_stream.stop()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    camera_stream.start()

    log.info("mars-pi server listening on http://%s:%d", cfg.HOST, cfg.PORT)
    log.info("  Stream   → http://<pi-ip>:%d/stream", cfg.PORT)
    log.info("  Snapshot → http://<pi-ip>:%d/snapshot", cfg.PORT)
    log.info("  Health   → http://<pi-ip>:%d/health", cfg.PORT)

    app.run(host=cfg.HOST, port=cfg.PORT, threaded=True, use_reloader=False)

