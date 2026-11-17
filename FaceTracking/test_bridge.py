import asyncio
import json
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path

from bridge import Bridge

FACETRACKING_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765

def _port_free() -> bool:
    with socket.socket() as s:
        return s.connect_ex((HOST, PORT)) != 0


class SyntheticSweepTests(unittest.TestCase):
    def setUp(self):
        self.bridge = Bridge(use_camera=False)

    def test_position_shape_and_range(self):
        for _ in range(10):
            position, source, camera_check = self.bridge.position()
            self.assertEqual(source, "Test/No Camera")
            self.assertFalse(camera_check)
            #x = 0.5 + 0.3*sin(...) -> [0.2, 0.8]; y = 0.5 + 0.2*sin(...) -> [0.3, 0.7]
            self.assertGreaterEqual(position[0], 0.2)
            self.assertLessEqual(position[0], 0.8)
            self.assertGreaterEqual(position[1], 0.3)
            self.assertLessEqual(position[1], 0.7)
            time.sleep(0.05)

    def test_event_contract(self):
        event = self.bridge.event()
        self.assertEqual(set(event), {"x", "y", "t", "source", "camera_check"})
        self.assertIsInstance(event["t"], int)
        self.assertEqual(event["source"], "Test/No Camera")
        self.assertFalse(event["camera_check"])
        self.assertGreaterEqual(event["x"], -1.0)
        self.assertLessEqual(event["x"], 1.0)
        self.assertGreaterEqual(event["y"], -1.0)
        self.assertLessEqual(event["y"], 1.0)

    def test_event_negates_the_normalized_offset(self):
        #fixed positions make the math deterministic
        self.bridge.position = lambda: ((0.6, 0.4), "Test/No Camera", False)
        self.bridge.calibrate()  # reference = (0.6, 0.4)
        self.bridge.position = lambda: ((0.7, 0.4), "Test/No Camera", False)
        event = self.bridge.event()
        #normalized dx = 0.1, and the bridge flips the sign for screen space
        self.assertAlmostEqual(event["x"], -0.1)
        self.assertAlmostEqual(event["y"], 0.0)

    def test_calibrate_makes_current_position_neutral(self):
        self.bridge.position = lambda: ((0.7, 0.4), "Test/No Camera", False)
        self.bridge.calibrate()
        event = self.bridge.event()
        self.assertAlmostEqual(event["x"], 0.0)
        self.assertAlmostEqual(event["y"], 0.0)


class WebSocketEndToEndTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if not _port_free():
            self.skipTest(f"{HOST}:{PORT} is in use - a bridge is already running")
        self.proc = subprocess.Popen(  #noqa: ASYNC220 - spawn only, does not block
            [sys.executable, "bridge.py"],
            cwd=FACETRACKING_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    async def asyncTearDown(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()

    async def _connect(self, timeout=30.0):
        from websockets.asyncio.client import connect

        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                out, err = self.proc.communicate(timeout=5)
                self.fail(f"bridge exited early:\n{err.decode()}\n{out.decode()}")
            try:
                #proxy=None: localhost traffic must never go through a proxy
                return await asyncio.wait_for(
                    connect(f"ws://{HOST}:{PORT}", proxy=None), 1.0
                )
            except (TimeoutError, OSError) as e:
                last_error = e
                await asyncio.sleep(0.25)
        self.fail(f"could not connect to the bridge: {last_error}")

    async def test_bridge_broadcasts_events(self):
        async with await self._connect() as ws:
            message = await asyncio.wait_for(ws.recv(), timeout=10)
            event = json.loads(message)
            self.assertEqual(set(event), {"x", "y", "t", "source", "camera_check"})
            self.assertEqual(event["source"], "Test/No Camera")
            self.assertGreaterEqual(event["x"], -1.0)
            self.assertLessEqual(event["x"], 1.0)
            self.assertGreaterEqual(event["y"], -1.0)
            self.assertLessEqual(event["y"], 1.0)

    async def test_bridge_keeps_streaming_after_calibrate(self):
        async with await self._connect() as ws:
            await asyncio.wait_for(ws.recv(), timeout=10)
            await ws.send(json.dumps({"type": "calibrate"}))
            #the server must survive calibration and keep broadcasting
            for _ in range(3):
                event = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
                self.assertIn("x", event)
                self.assertIn("y", event)

    async def test_bridge_ignores_malformed_messages(self):
        async with await self._connect() as ws:
            await asyncio.wait_for(ws.recv(), timeout=10)
            await ws.send("not json at all")
            await ws.send(json.dumps({"type": "nonsense"}))
            #stream keeps flowing after both
            event = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            self.assertIn("x", event)


if __name__ == "__main__":
    unittest.main()
