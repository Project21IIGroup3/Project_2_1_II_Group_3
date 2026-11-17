use std::process::{Child, Command};

//Start the Python bridge (tracking + parallax mapping) that serves the eye
//position on 127.0.0.1:8765. The child is returned so the shell can kill it
fn spawn_bridge() -> Option<Child> {
    let script = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()? // GUI/src-tauri -> GUI
        .parent()? // GUI -> repo root
        .join("FaceTracking")
        .join("bridge.py");

    let python = ["python3", "python"]
        .iter()
        .find(|p| Command::new(p).arg("--version").output().is_ok());

    python.and_then(|p| Command::new(p).arg(script.as_os_str()).spawn().ok())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let mut bridge = spawn_bridge();
    if bridge.is_none() {
        eprintln!(
            "pralax: could not start the Python bridge; \
             start it manually with `python FaceTracking/bridge.py`"
        );
    }

    let app = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    let _ = app.run(|_, _| {});

    //Sidecar lifecycle: stop the bridge when the app exits.
    if let Some(mut child) = bridge.take() {
        let _ = child.kill();
        let _ = child.wait();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::net::TcpStream;
    use std::time::{Duration, Instant};

    //The shell's whole job is to spawn a working bridge: the process must
    //start and serve its websocket on 127.0.0.1:8765. When no python is
    //available the test skips, so pure-Rust environments still pass.
    #[test]
    fn spawn_bridge_starts_and_listens() {
        let Some(child) = spawn_bridge() else {
            eprintln!("skipping: no python3/python on PATH");
            return;
        };

        //Reap the bridge even if the test fails midway.
        struct ChildGuard(Child);
        impl Drop for ChildGuard {
            fn drop(&mut self) {
                let _ = self.0.kill();
                let _ = self.0.wait();
            }
        }
        let mut child = ChildGuard(child);

        let deadline = Instant::now() + Duration::from_secs(30);
        loop {
            if let Some(status) = child.0.try_wait().expect("try_wait on bridge child") {
                panic!("bridge exited early with status {status}");
            }
            if TcpStream::connect(("127.0.0.1", 8765)).is_ok() {
                break;
            }
            if Instant::now() > deadline {
                panic!("bridge never started listening on 127.0.0.1:8765");
            }
            std::thread::sleep(Duration::from_millis(200));
        }
    }
}
