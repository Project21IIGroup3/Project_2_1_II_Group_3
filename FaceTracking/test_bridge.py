import time
import unittest

from bridge import Bridge


class SyntheticSweepTests(unittest.TestCase):
    def setUp(self):
        self.bridge = Bridge(use_camera=False)

    def test_position_stays_in_sweep_range(self):
        #x = 0.5 + 0.3*sin(...) -> [0.2, 0.8]; y = 0.5 + 0.2*sin(...) -> [0.3, 0.7]
        for _ in range(10):
            position, source = self.bridge.position()
            self.assertEqual(source, "synthetic")
            self.assertGreaterEqual(position[0], 0.2)
            self.assertLessEqual(position[0], 0.8)
            self.assertGreaterEqual(position[1], 0.3)
            self.assertLessEqual(position[1], 0.7)
            time.sleep(0.05)

    def test_event_is_normalized(self):
        for _ in range(10):
            event = self.bridge.event()
            self.assertEqual(event["source"], "synthetic")
            self.assertGreaterEqual(event["x"], -1.0)
            self.assertLessEqual(event["x"], 1.0)
            self.assertGreaterEqual(event["y"], -1.0)
            self.assertLessEqual(event["y"], 1.0)
            time.sleep(0.05)

    def test_calibrate_makes_current_position_neutral(self):
        time.sleep(0.1)
        self.bridge.calibrate()
        event = self.bridge.event()
        self.assertAlmostEqual(event["x"], 0.0, delta=0.01)
        self.assertAlmostEqual(event["y"], 0.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
