import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import cast
from threading import *
import cv2 as cv
import numpy as np
import time
from pathlib import Path
import threading
import time



BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode
LatestResult = None
CameraFlag = None
MODEL_PATH = Path(__file__).resolve().with_name('blaze_face_short_range.tflite')

def thread_function(options):
    with FaceDetector.create_from_options(options) as detector:
        
        
        cap = cv.VideoCapture(0)

        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        

        while cap.isOpened() and CameraFlag == 1:

            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
        
            frame = cv.flip(frame, 1)

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb) 
            detector.detect_async(mp_image, time.monotonic_ns() // 1_000_000)

        
            ''' __________ This is for drawing the vertex points on the camera, not needed for the actual project _______
            if LatestResult is not None:
                h, w = frame.shape[:2]
                for detection in LatestResult.detections:
                    bbox = detection.bounding_box
                    cv.rectangle(frame, (bbox.origin_x, bbox.origin_y),
                                (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height),
                                (0, 255, 0), 2, 16)
                    for kp in detection.keypoints:
                        cv.circle(frame, (int(kp.x * w), int(kp.y * h)), 4, (0, 0, 255), -1)
            
            if cv.waitKey(1) == ord('q'):
                break
            '''

        cap.release()
        cv.destroyAllWindows()
        



def print_result(result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
    print('face detector result: {}'.format(result))
    global LatestResult 
    LatestResult = result

def get_result():
    return LatestResult


def start_tracking():  
    global CameraFlag
    CameraFlag = 1   
    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result)

    x = threading.Thread(target=thread_function, args=(options,))
    x.daemon = True
    x.start() 

def stop_tracking():
    global CameraFlag
    CameraFlag = 0          

if __name__ == "__main__":
        start_tracking()   
    

