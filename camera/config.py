# Camera and server configuration for mars-pi
# Edit these values to match your setup.

# --- Server ---
HOST = "0.0.0.0"   # Listen on all network interfaces
PORT = 8000

# --- Stream ---
# Resolution for the live MJPEG stream.
# Pi Camera 3 native max is 4608x2592; keep stream resolution sane.
STREAM_WIDTH = 1280
STREAM_HEIGHT = 720
STREAM_FPS = 30

# JPEG quality for MJPEG frames (1–95; higher = better quality, more bandwidth)
STREAM_QUALITY = 85

# --- Snapshot ---
# Higher resolution single-frame capture (used by /snapshot endpoint)
SNAPSHOT_WIDTH = 2304
SNAPSHOT_HEIGHT = 1296

# --- Autofocus ---
# "ContinuousAfMode" keeps focus locked on the closest subject automatically.
# Set to "ManualAfMode" if you want to fix focus at a specific lens position.
AUTOFOCUS_MODE = "ContinuousAfMode"

# --- CORS ---
# Origins that are allowed to access the Pi API from a browser.
# Add your portfolio domain and any local dev origins here.
CORS_ORIGINS = [
    "https://travisjohnjones.com",
    "https://cosmonautjones.github.io",
    "http://localhost:3000",
    "http://localhost:8000",
]

