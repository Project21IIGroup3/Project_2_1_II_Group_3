import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import cast
import cv2 as cv
import numpy as np
import time
from pathlib import Path
import threading
import time

#Just a small setup for the face tracker, probably will have to change a lot to be able to implement it into the project

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode
LatestResult = None
MODEL_PATH = Path(__file__).resolve().with_name('blaze_face_short_range.tflite')

def thread_function(options):
    with FaceDetector.create_from_options(options) as detector:
 
        cap = cv.VideoCapture(0)

    

        fourcc = cv.VideoWriter_fourcc(*'XVID')
        out = cv.VideoWriter('output.avi', fourcc, 20.0, (640,  480))
  

   
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
            if LatestResult is not None:
                h, w = frame.shape[:2]
                for detection in LatestResult.detections:
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
        ap.release()
        out.release()
        cv.destroyAllWindows()
        detec.close()



def print_result(result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
    print('face detector result: {}'.format(result))
    global LatestResult 
    LatestResult = result

def get_result():
    return LatestResult

def start_tracking():      
    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result)

        x = threading.Thread(target=thread_function, args=(options))
        x.start() 
          

    if __name__ == "__main__":
        start_tracking()   
    

