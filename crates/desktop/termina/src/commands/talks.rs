//! The talks: the list, a new talk, a talk from another folder and the fields of `termina.json`.

use std::collections::HashMap;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use studio_engine::check_talk;

use crate::{in_thread, St};

#[tauri::command]
pub async fn talks(s: St<'_>) -> Result<Value, String> {
    let e = s.engine.clone();
    in_thread(move || e.json(["talks", "--json"])).await
}

/// Creates a talk with a title slide and a closing slide in `place`/`folder` (the talks folder and
/// charla-<title> if they are not given); returns `{id, title, path}`. `kind` "video" or "reel"
/// makes a video with a title scene and an end scene.
#[tauri::command]
#[allow(clippy::too_many_arguments)]
pub async fn new_talk(
    s: St<'_>,
    title: String,
    about: String,
    language: String,
    place: Option<String>,
    folder: Option<String>,
    kind: Option<String>,
) -> Result<Value, String> {
    let e = s.engine.clone();
    in_thread(move || {
        let mut args = vec![
            "new-talk".to_string(),
            "--json".into(),
            format!("--about={about}"),
            format!("--language={language}"),
        ];
        match kind.as_deref() {
            Some("video") => args.push("--video".into()),
            Some("reel") => args.push("--reel".into()),
            None | Some("slides") => {}
            Some(_) => return Err("The kind is slides, video or reel".into()),
        }
        if let Some(p) = place.filter(|p| !p.trim().is_empty()) {
            if !Path::new(&p).is_absolute() {
                return Err("Choose the folder that will hold it".into());
            }
            args.push(format!("--in={p}"));
        }
        if let Some(f) = folder.filter(|f| !f.trim().is_empty()) {
            args.push(format!("--folder={f}"));
        }
        // After “--” everything is title, even if it starts with a dash.
        args.extend(["--".into(), title]);
        e.json(args)
    })
    .await
}

/// Adds the talk in a folder (its own folder, its presentation/ or its termina.json) to the list;
/// returns `{id, title, path}`.
#[tauri::command]
pub async fn open_talk(s: St<'_>, path: String) -> Result<Value, String> {
    if !Path::new(&path).is_absolute() {
        return Err("Choose a folder".into());
    }
    let e = s.engine.clone();
    in_thread(move || e.json(["open".to_string(), "--json".into(), "--".into(), path])).await
}

/// Asks for a PowerPoint or a Beamer file and makes a talk from it in `place`; returns
/// `{id, title, path}`, or nothing if the dialog was closed.
#[tauri::command]
pub async fn import_talk(s: St<'_>, window: tauri::WebviewWindow, place: String) -> Result<Option<Value>, String> {
    if !Path::new(&place).is_absolute() {
        return Err("Choose the folder that will hold it".into());
    }
    let e = s.engine.clone();
    in_thread(move || {
        let picked = studio_shell::pick_file(&window, "Import a presentation", "Presentations", &["pptx", "tex"])?;
        let Some(file) = picked else { return Ok(None) };
        let file = file.display().to_string();
        e.json(["import".to_string(), "--json".into(), format!("--in={place}"), "--".into(), file]).map(Some)
    })
    .await
}

/// Changes what termina.json says (title, what it is about, resolution…); returns all its fields.
#[tauri::command]
pub async fn save_talk(s: St<'_>, talk: String, fields: HashMap<String, String>) -> Result<Value, String> {
    const FIELDS: [&str; 9] = ["title", "about", "author", "language", "resolution", "numbers", "kind", "music", "engine"];
    check_talk(&talk)?;
    let mut args = vec![talk, "info".to_string(), "--json".into()];
    for (k, v) in fields {
        if !FIELDS.contains(&k.as_str()) {
            return Err("A talk has no such field".into());
        }
        args.push(format!("--{k}={v}"));
    }
    let e = s.engine.clone();
    in_thread(move || e.json(args)).await
}

/// Takes a talk off the list; its folder stays as it is.
#[tauri::command]
pub async fn forget_talk(s: St<'_>, talk: String) -> Result<String, String> {
    check_talk(&talk)?;
    let e = s.engine.clone();
    in_thread(move || e.text([talk.as_str(), "forget"]).map(|t| t.trim().to_string())).await
}

/// Opens the talk's folder in the file explorer.
#[tauri::command]
pub fn show_talk_folder(s: St<'_>, talk: String) -> Result<(), String> {
    let pres = s.engine.presentation(&talk).ok_or("There is no such talk")?;
    studio_shell::open_folder(&pres)
}

/// The folder picker of the system, over the window. Returns `{path, empty}`, or nothing if it was closed.
#[tauri::command]
pub async fn pick_folder(
    window: tauri::WebviewWindow,
    title: String,
    start: Option<String>,
) -> Result<Option<Value>, String> {
    let (tx, rx) = std::sync::mpsc::channel();
    // A thread of its own: the dialog needs COM set up its way, and must not hold the window's.
    std::thread::spawn(move || {
        let title: String = title.chars().take(120).collect();
        let start = start.map(PathBuf::from).filter(|p| p.is_absolute() && p.is_dir());
        let picked = studio_shell::pick_folder(&window, &title, start).map(|folder| {
            folder.map(|p| {
                let empty = std::fs::read_dir(&p).map(|mut it| it.next().is_none()).unwrap_or(false);
                json!({ "path": p, "empty": empty })
            })
        });
        tx.send(picked).ok();
    });
    in_thread(move || rx.recv().map_err(|_| "The folder picker closed unexpectedly".to_string())?).await
}
