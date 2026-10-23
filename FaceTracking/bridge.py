"""
Bridge between the Python side (tracker + parallax mapping) and the GUI.

Serves the live, calibrated eye-position offset as JSON over a localhost-only
HTTP endpoint, so the Tauri frontend can drive the parallax effect:

    GET  /eye        -> {"x": -0.12, "y": 0.03, "t": 1761..., "source": "synthetic"}
    POST /calibrate  -> recalibrate the neutral reference at the current position

By default the position comes from a slow synthetic sweep, so no camera is
needed. Run `python bridge.py --camera` to drive it with the webcam tracker
(Face.py); it then uses the detected eye midpoint and falls back to the
synthetic sweep while no face is detected.

The server binds to 127.0.0.1 only, so nothing is exposed to the network.
Standard library only. The Tauri shell starts this process on launch and
kills it on exit (GUI/src-tauri/src/lib.rs); if the port is already taken
the script exits quietly.
"""

import argparse
import json
import math
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from parallax_mapping import ParallaxMapper, eye_midpoint

HOST = "127.0.0.1"
PORT = 8765


class Bridge:
    """Produces eye-position events from the camera tracker or a synthetic sweep."""

    def __init__(self, use_camera: bool) -> None:
        self.mapper = ParallaxMapper()
        self.use_camera = use_camera
        self._start = time.monotonic()
        if use_camera:
            import Face
            self._face = Face
            Face.start_tracking()
        else:
            self._face = None

    def position(self):
        """Current position in normalised 0..1 coords and its source name."""
        if self._face is not None:
            midpoint = eye_midpoint(self._face.get_result())
            if midpoint is not None:
                return midpoint, "camera"
        t = time.monotonic() - self._start
        x = 0.5 + 0.3 * math.sin(0.5 * t)
        y = 0.5 + 0.2 * math.sin(0.23 * t + 1.0)
        return (x, y), "synthetic"

    def event(self):
        """One JSON-ready event: reference-relative, normalised eye offset."""
        position, source = self.position()
        x, y = self.mapper.normalized(position)
        return {"x": x, "y": y, "t": int(time.time() * 1000), "source": source}

    def calibrate(self) -> None:
        position, _ = self.position()
        self.mapper.calibrate(position)


class Handler(BaseHTTPRequestHandler):
    bridge: Bridge = None  # injected by main()

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/eye":
            self._send_json(self.bridge.event())
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self) -> None:
        if self.path == "/calibrate":
            self.bridge.calibrate()
            self._send_json({"ok": True})
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, *args) -> None:
        pass  # keep the console quiet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", action="store_true",
                        help="use the webcam tracker instead of the synthetic sweep")
    args = parser.parse_args()

    Handler.bridge = Bridge(use_camera=args.camera)
    source = "webcam tracker" if args.camera else "synthetic sweep (no camera)"

    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        print(f"{HOST}:{PORT} already in use - another bridge is running; exiting.")
        return

    print(f"Bridge listening on http://{HOST}:{PORT}/eye ({source}). Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
