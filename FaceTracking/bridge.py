"""HTTP bridge between the face tracker and the GUI."""

import argparse
import json
import math
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from parallax_mapping import ParallaxMapper, eye_midpoint

HOST = "127.0.0.1"
PORT = 8765

class Bridge:
    def __init__(self, use_camera: bool):
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
        if self._face is not None:
            midpoint = eye_midpoint(self._face.get_result())
            if midpoint is not None:
                return midpoint, "camera"
        t = time.monotonic() - self._start
        x = 0.5 + 0.3 * math.sin(0.5 * t)
        y = 0.5 + 0.2 * math.sin(0.23 * t + 1.0)
        return (x, y), "synthetic"

    def event(self):
        position, source = self.position()
        x, y = self.mapper.normalized(position)
        return {"x": x, "y": y, "t": int(time.time() * 1000), "source": source}

    def calibrate(self):
        position, _ = self.position()
        self.mapper.calibrate(position)

class Handler(BaseHTTPRequestHandler):
    bridge: Bridge = None  #set by main()

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  #wouldnt work otherwise
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/eye":
            self._send_json(self.bridge.event())
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self):
        if self.path == "/calibrate":
            self.bridge.calibrate()
            self._send_json({"ok": True})
        else:
            self._send_json({"error": "not found"}, status=404)

    def log_message(self, *args):
        pass  #don't spam the console with request logs


def main():
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

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
