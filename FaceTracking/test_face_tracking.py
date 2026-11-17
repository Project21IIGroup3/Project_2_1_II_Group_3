import unittest

from Face import FaceTracking


class _Keypoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class _Detection:
    def __init__(self, keypoints):
        self.keypoints = keypoints


class _Result:
    def __init__(self, detections):
        self.detections = detections


class FaceTrackingDefaultsTests(unittest.TestCase):
    def test_default_configuration(self):
        tracker = FaceTracking()
        self.assertEqual(tracker.get_camera_index(), 0)
        self.assertEqual(tracker.get_fps(), 20.0)
        self.assertTrue(tracker.get_output_path().endswith("output.avi"))

    def test_custom_configuration(self):
        tracker = FaceTracking(camera_index=2, output_path="~/test.avi", fps=30.0)
        self.assertEqual(tracker.get_camera_index(), 2)
        self.assertEqual(tracker.get_fps(), 30.0)
        self.assertIn("test.avi", tracker.get_output_path())


class EyeMidpointTests(unittest.TestCase):
    def setUp(self):
        self.tracker = FaceTracking()

    def test_none_result_returns_none(self):
        self.assertIsNone(self.tracker.eye_midpoint())

    def test_no_detections_returns_none(self):
        self.tracker.latest_result = _Result([])
        self.assertIsNone(self.tracker.eye_midpoint())

    def test_too_few_keypoints_returns_none(self):
        self.tracker.latest_result = _Result([_Detection([_Keypoint(0.1, 0.2)])])
        self.assertIsNone(self.tracker.eye_midpoint())

    def test_midpoint_averages_the_eyes(self):
        self.tracker.latest_result = _Result(
            [_Detection([_Keypoint(0.1, 0.2), _Keypoint(0.3, 0.6)])]
        )
        self.assertEqual(self.tracker.eye_midpoint(), (0.2, 0.4))

    def test_first_detection_is_used(self):
        first = _Detection([_Keypoint(0.1, 0.1), _Keypoint(0.3, 0.3)])
        second = _Detection([_Keypoint(0.9, 0.9), _Keypoint(0.9, 0.9)])
        self.tracker.latest_result = _Result([first, second])
        self.assertEqual(self.tracker.eye_midpoint(), (0.2, 0.2))


if __name__ == "__main__":
    unittest.main()
