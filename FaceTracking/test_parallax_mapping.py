import math
import unittest

from parallax_mapping import K_PX, ParallaxMapper, eye_midpoint


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


class ParallaxMapperCalibrationTests(unittest.TestCase):
    def test_normalized_is_zero_at_reference(self):
        mapper = ParallaxMapper()
        mapper.calibrate((0.5, 0.5))
        self.assertEqual(mapper.normalized((0.5, 0.5)), (0.0, 0.0))

    def test_normalized_measures_offset_from_reference(self):
        mapper = ParallaxMapper()
        mapper.calibrate((0.5, 0.5))
        dx, dy = mapper.normalized((0.6, 0.4))
        self.assertAlmostEqual(dx, 0.1)
        self.assertAlmostEqual(dy, -0.1)

    def test_normalized_clamps_to_unit_range(self):
        mapper = ParallaxMapper()
        mapper.calibrate((0.5, 0.5))
        self.assertEqual(mapper.normalized((1.6, -0.6)), (1.0, -1.0))

    def test_normalized_auto_calibrates_on_first_call(self):
        mapper = ParallaxMapper()
        #first call has no reference yet, so it calibrates and returns zero
        self.assertEqual(mapper.normalized((0.3, 0.7)), (0.0, 0.0))
        #from now on the same position is the neutral point
        self.assertEqual(mapper.normalized((0.3, 0.7)), (0.0, 0.0))
        dx, dy = mapper.normalized((0.4, 0.7))
        self.assertAlmostEqual(dx, 0.1)
        self.assertAlmostEqual(dy, 0.0)


class ParallaxMapperSmoothingTests(unittest.TestCase):
    def test_update_applies_ema_to_fresh_offset(self):
        mapper = ParallaxMapper(smoothing=0.1)
        mapper.calibrate((0.5, 0.5))
        x, y = mapper.update((0.6, 0.5))
        self.assertAlmostEqual(x, 0.01)  #0.1 * 0.1 + 0.9 * 0
        self.assertAlmostEqual(y, 0.0)

    def test_update_converges_toward_target(self):
        mapper = ParallaxMapper(smoothing=0.1)
        mapper.calibrate((0.5, 0.5))
        for _ in range(100):
            x, y = mapper.update((0.6, 0.5))
        #after n steps: dx * (1 - (1 - a)^n) -> dx
        self.assertAlmostEqual(x, 0.1, places=3)
        self.assertAlmostEqual(y, 0.0, places=3)

    def test_calibrate_resets_smoothing_state(self):
        mapper = ParallaxMapper(smoothing=0.1)
        mapper.calibrate((0.5, 0.5))
        mapper.update((0.9, 0.9))  #builds up a smoothed offset
        mapper.calibrate((0.9, 0.9)) #new neutral point
        x, y = mapper.update((0.9, 0.9))
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)

    def test_axes_are_independent(self):
        mapper = ParallaxMapper(smoothing=0.5)
        mapper.calibrate((0.5, 0.5))
        x, y = mapper.update((0.7, 0.5))
        self.assertAlmostEqual(x, 0.1)
        self.assertAlmostEqual(y, 0.0)


class ParallaxMapperLayerOffsetTests(unittest.TestCase):
    def test_offset_scales_with_intensity_and_depth(self):
        mapper = ParallaxMapper(intensity=0.5, depth=20.0)
        mapper.calibrate((0.5, 0.5))
        mapper.update((0.6, 0.5))
        scale = 0.5 * K_PX * 20.0 / 20.0
        x, y = mapper.layer_offset(20.0)
        self.assertAlmostEqual(x, 0.01 * scale)
        self.assertAlmostEqual(y, 0.0)

    def test_zero_smoothed_offset_gives_zero_layer_offset(self):
        mapper = ParallaxMapper()
        mapper.calibrate((0.5, 0.5))
        self.assertEqual(mapper.layer_offset(20.0), (0.0, 0.0))

    def test_layer_depth_changes_scale(self):
        mapper = ParallaxMapper(intensity=1.0, depth=20.0)
        mapper.calibrate((0.5, 0.5))
        mapper.update((0.6, 0.5))
        near = mapper.layer_offset(20.0)[0]
        far = mapper.layer_offset(40.0)[0]
        self.assertAlmostEqual(near, 2.0 * far)

    def test_zero_layer_depth_does_not_divide_by_zero(self):
        mapper = ParallaxMapper()
        mapper.calibrate((0.5, 0.5))
        mapper.update((0.6, 0.5))
        offset = mapper.layer_offset(0.0)
        self.assertTrue(math.isfinite(offset[0]))
        self.assertTrue(math.isfinite(offset[1]))


class EyeMidpointTests(unittest.TestCase):
    def test_none_result_returns_none(self):
        self.assertIsNone(eye_midpoint(None))

    def test_no_detections_returns_none(self):
        self.assertIsNone(eye_midpoint(_Result([])))

    def test_too_few_keypoints_returns_none(self):
        result = _Result([_Detection([_Keypoint(0.1, 0.2)])])
        self.assertIsNone(eye_midpoint(result))

    def test_midpoint_averages_the_eyes(self):
        result = _Result(
            [_Detection([_Keypoint(0.1, 0.2), _Keypoint(0.3, 0.6)])]
        )
        self.assertEqual(eye_midpoint(result), (0.2, 0.4))

    def test_first_detection_is_used(self):
        first = _Detection([_Keypoint(0.1, 0.1), _Keypoint(0.3, 0.3)])
        second = _Detection([_Keypoint(0.9, 0.9), _Keypoint(0.9, 0.9)])
        result = _Result([first, second])
        self.assertEqual(eye_midpoint(result), (0.2, 0.2))


if __name__ == "__main__":
    unittest.main()
