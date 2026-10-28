use std::process::{Child, Command};

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// Start the Python bridge (tracking + parallax mapping) that serves the eye
/// position on 127.0.0.1:8765. The child is returned so the shell can kill it
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
        .invoke_handler(tauri::generate_handler![greet])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    let result = app.run(|_, _| {});

    // Sidecar lifecycle: stop the bridge when the app exits.
    if let Some(mut child) = bridge.take() {
        let _ = child.kill();
        let _ = child.wait();
    }

    //result.expect("error while running tauri application");
}
