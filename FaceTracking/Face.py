import sys
import threading
import time
from pathlib import Path

import cv2 as cv
import mediapipe as mp

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

    def _print_result(self, result: FaceDetectorResult, _output_image: mp.Image, _timestamp_ms: int, ) -> None:
        print(f'face detector result: {result}')
        self.latest_result = result

    def _face_detection(self, options):
        with FaceDetector.create_from_options(options) as detector:
            cap = cv.VideoCapture(self.camera_index)
            fourcc = cv.VideoWriter_fourcc(*'XVID')
            out = cv.VideoWriter(self.output_path, fourcc, self.fps, (640, 480))

            if not cap.isOpened():
                print("Cannot open camera")
                sys.exit()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                detector.detect_async(mp_image, time.monotonic_ns() // 1_000_000)

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

        thread = threading.Thread(target=self._face_detection, args=(options,))
        thread.start()
        return self

    def eye_midpoint(self) -> tuple[float, float] | None:
        result = self.latest_result
        if result is None or not getattr(result, "detections", None):
            return None
        detection = result.detections[0]
        if len(detection.keypoints) < 2:
            return None
        left_eye = detection.keypoints[0]
        right_eye = detection.keypoints[1]
        return ((left_eye.x + right_eye.x) / 2.0, (left_eye.y + right_eye.y) / 2.0)

    def get_camera_index(self):
        return self.camera_index
    
    def get_output_path(self):
        return str(Path(self.output_path).expanduser().resolve())
    
    def get_fps(self):
        return self.fps

class ParallaxMapper:
    def __init__(self, intensity: float = 0.5, depth: float = 20.0, smoothing: float = 0.1):
        self.intensity = intensity  #overall effect strength
        self.depth = depth  #reference depth in px
        self.smoothing = smoothing  #EMA factor alpha
        self._reference: tuple[float, float] | None = None  #neutral position
        self._smoothed: tuple[float, float] = (0.0, 0.0)  #last smoothed offset

    def calibrate(self, position: tuple[float, float]):
        self._reference = position
        self._smoothed = (0.0, 0.0)

    def normalized(self, position: tuple[float, float]) -> tuple[float, float]:
        if self._reference is None:
            self.calibrate(position)
        dx = position[0] - self._reference[0]
        dy = position[1] - self._reference[1]
        return (max(-1.0, min(1.0, dx)), max(-1.0, min(1.0, dy)))

    def update(self, position: tuple[float, float]) -> tuple[float, float]:
        dx, dy = self.normalized(position)
        a = self.smoothing
        self._smoothed = (
            a * dx + (1.0 - a) * self._smoothed[0],
            a * dy + (1.0 - a) * self._smoothed[1],
        )
        return self._smoothed

    def layer_offset(self, layer_depth: float) -> tuple[float, float]:
        scale = self.intensity * K_PX * self.depth / max(layer_depth, 1e-6)
        return (self._smoothed[0] * scale, self._smoothed[1] * scale)
