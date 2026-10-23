"""
Face-to-parallax mapping prototype (phase 1, Sotiris).

Maps a live position (the eye position, or the mouse standing in for it) to
per-layer parallax offsets.

    position (x, y) in normalised 0..1 coordinates
      -> subtract calibration reference point
      -> EMA smoothing (settings.smoothing = alpha)
      -> layer offset px = intensity * eye * K_PX * depth / layer_depth

Status: CONNECTED to the GUI. FaceTracking/bridge.py serves the mapped,
normalised offset over a localhost-only HTTP endpoint (GET /eye), and the
Tauri frontend polls it to move the artwork - the middle-end between the
tracker and the GUI. `python bridge.py --camera` drives it with the webcam
tracker (Face.py, via eye_midpoint(get_result())); by default it uses a
synthetic sweep, so no camera is needed. demo() below prints the mapping
for synthetic positions.

The three tuning parameters match the GUI overlay's ParallaxSettings
(intensity / depth / smoothing), so the interface already lines up.
"""

from typing import Optional, Tuple

# Pixels of displacement per normalised position unit for a layer at the
# configured `depth`. Tuned by feel in phase 1; revisit with T2.6 (calibration).
K_PX = 500.0


class ParallaxMapper:
    """Turns positions into per-layer parallax offsets, relative to a
    calibrated reference point."""

    def __init__(self, intensity: float = 0.5, depth: float = 20.0, smoothing: float = 0.1):
        self.intensity = intensity   # overall effect strength  (GUI: intensity slider)
        self.depth = depth           # reference depth in px    (GUI: depth slider)
        self.smoothing = smoothing   # EMA factor alpha         (GUI: smoothing slider)
        self._reference: Optional[Tuple[float, float]] = None  # neutral position
        self._smoothed: Tuple[float, float] = (0.0, 0.0)       # last smoothed offset

    def calibrate(self, position: Tuple[float, float]) -> None:
        """Store `position` as the neutral reference point (the user looks
        straight at the screen centre while calibrating). Resets the smoothed
        offset so the effect starts from zero."""
        self._reference = position
        self._smoothed = (0.0, 0.0)

    def normalized(self, position: Tuple[float, float]) -> Tuple[float, float]:
        """Deviation of `position` from the reference point, clamped to
        [-1, 1]. Does not touch the smoothed state (used by bridge.py)."""
        if self._reference is None:
            self.calibrate(position)
        dx = position[0] - self._reference[0]
        dy = position[1] - self._reference[1]
        return (max(-1.0, min(1.0, dx)), max(-1.0, min(1.0, dy)))

    def update(self, position: Tuple[float, float]) -> Tuple[float, float]:
        """Feed a new position (normalised 0..1 coords); returns the
        EMA-smoothed offset relative to the reference point."""
        dx, dy = self.normalized(position)
        a = self.smoothing
        self._smoothed = (
            a * dx + (1.0 - a) * self._smoothed[0],
            a * dy + (1.0 - a) * self._smoothed[1],
        )
        return self._smoothed

    def layer_offset(self, layer_depth: float) -> Tuple[float, float]:
        """Pixel displacement for a content layer at `layer_depth` px.

        Near layers (small depth) move more than far layers, which is what
        creates the parallax illusion."""
        scale = self.intensity * K_PX * self.depth / max(layer_depth, 1e-6)
        return (self._smoothed[0] * scale, self._smoothed[1] * scale)


def eye_midpoint(result) -> Optional[Tuple[float, float]]:
    """Mean of the two eye keypoints of the first detection in a MediaPipe
    FaceDetectorResult (keypoints 0 and 1 are the eyes), in normalised image
    coordinates (0..1). Returns None when no face is detected.

    This is the integration point for the webcam tracker: in phase 2 it
    converts the output of Face.py's get_result() into a position for
    ParallaxMapper. It touches only public fields, so it can be tested
    without mediapipe installed."""
    if result is None or not getattr(result, "detections", None):
        return None
    detection = result.detections[0]
    if len(detection.keypoints) < 2:
        return None
    left_eye = detection.keypoints[0]
    right_eye = detection.keypoints[1]
    return ((left_eye.x + right_eye.x) / 2.0, (left_eye.y + right_eye.y) / 2.0)


def demo() -> None:
    """Standalone demo on synthetic positions - no camera, no window needed.

    Simulates the position sweeping left -> centre -> right with a small
    jitter, prints the smoothed offset and the resulting layer offsets (near
    layers move most), then recalibrates and shows the offset resetting to
    zero."""
    import math

    mapper = ParallaxMapper()  # defaults match the GUI overlay

    print("Face-to-parallax mapping prototype")
    print("(synthetic demo; the same mapping drives the GUI through bridge.py)")
    print(f"settings: intensity={mapper.intensity}, depth={mapper.depth}px, "
          f"smoothing={mapper.smoothing}\n")

    path = [0.5 + 0.3 * math.sin(t) + 0.02 * math.sin(13.0 * t)
            for t in (0.5 * i for i in range(13))]

    print("step | position        | smoothed offset | layer offsets px (depth 10 / 20 / 80)")
    print("-" * 82)
    for i, x in enumerate(path):
        position = (x, 0.5)
        offset = mapper.update(position)
        near, mid, far = (mapper.layer_offset(d) for d in (10.0, 20.0, 80.0))
        print(f"{i:4d} | ({x:6.3f}, 0.500) | ({offset[0]:+7.4f},{offset[1]:+7.4f}) |"
              f" ({near[0]:+6.1f},{near[1]:+6.1f}) ({mid[0]:+6.1f},{mid[1]:+6.1f})"
              f" ({far[0]:+6.1f},{far[1]:+6.1f})")

    print("\nRecalibrating at the current position ...")
    mapper.calibrate((path[-1], 0.5))
    print(f"offset after recalibration: {mapper.update((path[-1], 0.5))}"
          f"  (should be (0.0, 0.0))")


if __name__ == "__main__":
    demo()
