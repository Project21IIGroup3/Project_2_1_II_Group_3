# Pralax - workflow

- input: synthetic sweep in bridge.py, or the webcam (SYN / CAM)
- processing: camera loop, BGR->RGB, BlazeFace detection (LOOP / RGB / DET / STORE)
- algorithm: calibration + EMA smoothing + parallax mapping (MAP)
- output/interaction: bridge WebSocket, SvelteKit UI, artwork translate (BRIDGE / UI / ENG / DISP)

Solid arrows: data flow. Dotted arrow: process lifecycle only (the Rust shell starts and stops the bridge).

```mermaid
flowchart TD
    SYN["Position source (default)<br/>synthetic sweep in bridge.py, no camera"] --> MAP["Face-to-parallax mapping (middle-end)<br/>Face.py: calibration reference + normalised offset"]
    CAM["Webcam<br/>640x480 @ 30 FPS"] --> LOOP["Camera loop (own thread)<br/>OpenCV VideoCapture(0)"]
    LOOP --> RGB["Colour conversion<br/>BGR to RGB"]
    RGB --> DET["MediaPipe FaceDetector<br/>BlazeFace short-range (TFLite)<br/>detect_async + result callback"]
    DET --> STORE["latest_result<br/>read via eye_midpoint(); output.avi"]
    STORE -->|"bridge.py --camera"| MAP
    MAP --> BRIDGE["Python bridge (bridge.py)<br/>localhost-only WebSocket: ws://127.0.0.1:8765<br/>JSON events @ 60 Hz, calibrate message"]
    RUST["Tauri Rust shell<br/>spawns bridge.py on launch, kills it on exit"] -.-> BRIDGE
    BRIDGE --> UI["SvelteKit UI<br/>eye.ts opens the WebSocket, store updates<br/>settings overlay: intensity / depth / smoothing"]
    UI --> ENG["Parallax engine (connected)<br/>off-axis projection: artwork shifts with the smoothed eye offset"]
    ENG --> DISP["Display (desktop window)"]
    UI --> ART["Scene assets<br/>3D models (static/models)"]
    ART --> ENG
```
