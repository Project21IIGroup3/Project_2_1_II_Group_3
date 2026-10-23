from typing import Optional, Tuple

#Pixels of displacement per normalised position unit for a layer at the
#configured `depth`. Tuned by feel in phase 1; revisit with T2.6 (calibration).
K_PX = 500.0


class ParallaxMapper:
    def __init__(self, intensity: float = 0.5, depth: float = 20.0, smoothing: float = 0.1):
        self.intensity = intensity  #overall effect strength
        self.depth = depth  #reference depth in px
        self.smoothing = smoothing  #EMA factor alpha
        self._reference: Optional[Tuple[float, float]] = None  #neutral position
        self._smoothed: Tuple[float, float] = (0.0, 0.0)  #last smoothed offset

    def calibrate(self, position: Tuple[float, float]):
        self._reference = position
        self._smoothed = (0.0, 0.0)

    def normalized(self, position: Tuple[float, float]) -> Tuple[float, float]:
        if self._reference is None:
            self.calibrate(position)
        dx = position[0] - self._reference[0]
        dy = position[1] - self._reference[1]
        return (max(-1.0, min(1.0, dx)), max(-1.0, min(1.0, dy)))

    def update(self, position: Tuple[float, float]) -> Tuple[float, float]:
        dx, dy = self.normalized(position)
        a = self.smoothing
        self._smoothed = (
            a * dx + (1.0 - a) * self._smoothed[0],
            a * dy + (1.0 - a) * self._smoothed[1],
        )
        return self._smoothed

    def layer_offset(self, layer_depth: float) -> Tuple[float, float]:
        scale = self.intensity * K_PX * self.depth / max(layer_depth, 1e-6)
        return (self._smoothed[0] * scale, self._smoothed[1] * scale)


def eye_midpoint(result) -> Optional[Tuple[float, float]]:
    if result is None or not getattr(result, "detections", None):
        return None
    detection = result.detections[0]
    if len(detection.keypoints) < 2:
        return None
    left_eye = detection.keypoints[0]
    right_eye = detection.keypoints[1]
    return ((left_eye.x + right_eye.x) / 2.0, (left_eye.y + right_eye.y) / 2.0)
