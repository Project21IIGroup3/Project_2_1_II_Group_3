"""HTTP bridge between the face tracker and the GUI."""

import argparse
import asyncio
import json
import math
import time
from websockets.asyncio.server import broadcast, serve

from Face import FaceTracking, ParallaxMapper

HOST = "127.0.0.1"
PORT = 8765

class Bridge:
    def __init__(self, use_camera: bool):
        self._last = (0.5,0.5)
        self.mapper = ParallaxMapper()
        self.use_camera = use_camera
        self._start = time.monotonic()
        if use_camera:
            self._face = FaceTracking()
            self._face.start_tracking()
        else:
            self._face = None

    def position(self):
        if self._face is not None:
            midpoint = self._face.eye_midpoint()
            if midpoint is not None:
                self._last = midpoint
                return midpoint, "camera", True
            else:
                return self._last, "camera", False
        t = time.monotonic() - self._start
        x = 0.5 + 0.3 * math.sin(0.5 * t)
        y = 0.5 + 0.2 * math.sin(0.23 * t + 1.0)
        return (x, y), "Test/No Camera", False

    def event(self):
        position, source, camera_check = self.position()
        x, y = self.mapper.normalized(position)
        return {"x": -x, "y": -y, "t": int(time.time() * 1000), "source": source, "camera_check": camera_check}

    def calibrate(self):
        position, _ = self.position()
        self.mapper.calibrate(position)

bridge: Bridge = None

async def handler(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            continue
        if data.get("type") == "calibrate":
            bridge.calibrate()

async def broadcast_loop(server):
    while True:
        broadcast(server.connections, json.dumps(bridge.event()))
        await asyncio.sleep(1 / 60)

async def main():
    global bridge
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", action="store_true",
                        help="use the webcam tracker instead of the synthetic sweep")
    args = parser.parse_args()

    bridge = Bridge(use_camera=args.camera)

    source = "webcam tracker" if args.camera else "Testing/No Camera"

    try:    
        server = await serve(handler,HOST,PORT)
        await server.serve_forever
    except OSError:
        print(f"{HOST}:{PORT} already in use - another bridge is running; exiting.")
        return
        
    print(f"Bridge on ws://{HOST}:{PORT} using {source}", flush=True)
    async with server:
        asyncio.create_task(broadcast_loop(server))
        await server.serve_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass