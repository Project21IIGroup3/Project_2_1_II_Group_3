import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Any, cast
import cv2 as cv
import numpy as np
import time
from pathlib import Path
import threading
from typing import Optional, Tuple

#Just a small setup for the face tracker, probably will have to change a lot to be able to implement it into the project

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode
MODEL_PATH = Path(__file__).resolve().with_name('blaze_face_short_range.tflite')
K_PX = 500.0

class FaceTracking:
    def __init__(self, camera_index: int = 0, output_path: str = 'output.avi', fps: float = 20.0):
        self.camera_index = camera_index
        self.output_path = output_path
        self.fps = fps
        self.latest_result = None
        self._thread = None

    def _print_result(self, result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
        print('face detector result: {}'.format(result))
        self.latest_result = result

    def get_result(self):
        return self.latest_result

    def _thread_function(self, options):
        with FaceDetector.create_from_options(options) as detector:
            cap = cv.VideoCapture(self.camera_index)
            fourcc = cv.VideoWriter_fourcc(*'XVID')
            out = cv.VideoWriter(self.output_path, fourcc, self.fps, (640, 480))

            if not cap.isOpened():
                print("Cannot open camera")
                exit()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                detector.detect_async(mp_image, time.monotonic_ns() // 1_000_000)

                ''' __________ This is for drawing the vertex points on the camera, not needed for the actual project _______
                if self.latest_result is not None:
                    h, w = frame.shape[:2]
                    for detection in self.latest_result.detections:
                        bbox = detection.bounding_box
                        cv.rectangle(frame, (bbox.origin_x, bbox.origin_y),
                                    (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height),
                                    (0, 255, 0), 2, 16)
                        for kp in detection.keypoints:
                            cv.circle(frame, (int(kp.x * w), int(kp.y * h)), 4, (0, 0, 255), -1)
                '''

                frame = cv.flip(frame, 1)
                out.write(frame)

                if cv.waitKey(1) == ord('q'):
                    break

            cap.release()
            out.release()
            cv.destroyAllWindows()

    def start_tracking(self):
        options = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self._print_result)

        self._thread = threading.Thread(target=self._thread_function, args=(options,))
        self._thread.start()
        return self


if __name__ == "__main__":
    FaceTracking().start_tracking()


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