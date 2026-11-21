//! The slides of a talk: their status, the renders, the changes, the review and the export.

use serde_json::Value;

use studio_engine::jobs::Summary;
use studio_engine::{check_talk, QUALITIES};

use crate::{in_thread, St};

/// The formats of an export, and the option of studio.py for each one.
const EXPORTS: [(&str, &[&str]); 7] = [
    ("narrated", &["--narrated"]),
    ("html", &[]),
    ("pdf", &["--pdf"]),
    ("mp4", &["--mp4"]),
    ("gif", &["--gif"]),
    ("pptx", &["--pptx"]),
    ("package", &["--package"]),
];

#[tauri::command]
pub async fn status(s: St<'_>, talk: String) -> Result<Value, String> {
    check_talk(&talk)?;
    let e = s.engine.clone();
    in_thread(move || e.status(&talk)).await
}

#[tauri::command]
pub fn jobs(s: St<'_>) -> Vec<Summary> {
    s.jobs.summary()
}

/// `what` is a list of slides, "pending" or "all". `quality` is the talk's; the slides with a
/// resolution of their own come out in theirs.
#[tauri::command]
pub fn render(s: St<'_>, talk: String, what: Value, quality: String) -> Result<(), String> {
    check_talk(&talk)?;
    if !QUALITIES.contains(&quality.as_str()) {
        return Err("The quality is 480p, 720p or 1080p".into());
    }
    let mut args = vec![talk.clone(), "render".to_string(), format!("--quality={quality}")];
    let title = match &what {
        Value::String(w) if w == "pending" => {
            args.push("--pending".into());
            "Render of the pending slides".to_string()
        }
        Value::String(w) if w == "all" => {
            args.push("--all".into());
            "Render of the whole talk".to_string()
        }
        Value::Array(v) => {
            let names: Vec<String> = v.iter().filter_map(|x| x.as_str().map(String::from)).collect();
            let title = match names.as_slice() {
                [] => return Err("There are no slides to render".into()),
                [one] => format!("Render of {one} ({quality})"),
                many => format!("Render of {} slides", many.len()),
            };
            // After “--” a slide is always a slide, even if its name starts with a dash.
            args.push("--".into());
            args.extend(names);
            title
        }
        _ => return Err("I don't know what to render".into()),
    };
    s.jobs.add(&talk, &title, args);
    Ok(())
}

/// Changes to the talk: new, move, rename, group, duplicate, hide, restore, delete, resolution and
/// the speaker notes, and the 8-bit music of a video. Returns what studio.py answered (for “new” and
/// “duplicate”, a JSON with the created slide).
#[tauri::command]
pub async fn edit(s: St<'_>, talk: String, args: Vec<String>) -> Result<String, String> {
    const ORDERS: [&str; 15] = [
        "new", "move", "rename", "group", "duplicate", "hide", "restore", "delete", "resolution", "speaker",
        "theme", "move-object", "retext", "insert", "chiptune",
    ];
    check_talk(&talk)?;
    if !args.first().is_some_and(|o| ORDERS.contains(&o.as_str())) {
        return Err("That order does not exist".into());
    }
    let e = s.engine.clone();
    in_thread(move || {
        let mut all = vec![talk];
        all.extend(args);
        e.text(&all).map(|t| t.trim().to_string())
    })
    .await
}

/// What the render of the slide at `line` shows on each pause, as `{pauses, frame, fresh}`.
#[tauri::command]
pub async fn objects(s: St<'_>, talk: String, line: u32) -> Result<Value, String> {
    check_talk(&talk)?;
    let e = s.engine.clone();
    in_thread(move || e.json([talk, "objects".to_string(), format!("--line={line}")])).await
}

/// Asks for a picture and adds it to the slide at `line`, on `pause`, at `at` (“x,y”). Returns
/// what the engine answered, or nothing if the dialog was closed.
#[tauri::command]
pub async fn insert_picture(
    s: St<'_>,
    window: tauri::WebviewWindow,
    talk: String,
    line: u32,
    pause: u32,
    at: String,
) -> Result<Option<String>, String> {
    check_talk(&talk)?;
    let e = s.engine.clone();
    in_thread(move || {
        let picked = studio_shell::pick_file(&window, "Choose a picture", "Pictures", &["png", "jpg", "jpeg"])?;
        let Some(file) = picked else { return Ok(None) };
        let args = [
            talk,
            "insert".to_string(),
            "--kind=picture".into(),
            format!("--line={line}"),
            format!("--pause={pause}"),
            format!("--at={at}"),
            format!("--file={}", file.display()),
        ];
        e.text(args).map(|t| Some(t.trim().to_string()))
    })
    .await
}

/// Finds text in the slides and the speaker notes, as `{matches, replaced}`. With `replace`,
/// replaces each match.
#[tauri::command]
pub async fn find(
    s: St<'_>,
    talk: String,
    query: String,
    replace: Option<String>,
    case: bool,
    word: bool,
) -> Result<Value, String> {
    check_talk(&talk)?;
    let e = s.engine.clone();
    in_thread(move || {
        let mut args = vec![talk, "find".to_string()];
        if let Some(r) = replace {
            args.push(format!("--replace={r}"));
        }
        if case {
            args.push("--case".into());
        }
        if word {
            args.push("--word".into());
        }
        // After “--” everything is the text to find, even if it starts with a dash.
        args.extend(["--".into(), query]);
        e.json(args)
    })
    .await
}

/// Exports the talk (HTML, PDF, MP4, PowerPoint or its package) or, with `slide`, one slide (MP4 or GIF).
#[tauri::command]
pub fn export(s: St<'_>, talk: String, format: String, slide: Option<String>) -> Result<(), String> {
    check_talk(&talk)?;
    let Some((_, option)) = EXPORTS.iter().find(|(name, _)| *name == format) else {
        return Err("The export is HTML, PDF, MP4, GIF, PowerPoint, a narrated video or a package".into());
    };
    let mut args = vec![talk.clone(), "export".to_string()];
    args.extend(option.iter().map(|o| o.to_string()));
    let mut title = format!("Export {talk} ({})", format.to_uppercase());
    if let Some(slide) = slide {
        if !matches!(format.as_str(), "mp4" | "gif") {
            return Err("One slide exports as MP4 or GIF".into());
        }
        title = format!("Export {slide} ({})", format.to_uppercase());
        // After “--” a slide is always a slide, even if its name starts with a dash.
        args.extend(["--".into(), slide]);
    } else if format == "gif" {
        return Err("A GIF is of one slide".into());
    }
    s.jobs.add(&talk, &title, args);
    Ok(())
}

#[tauri::command]
pub fn cancel(s: St<'_>, id: u64) {
    s.jobs.cancel(id);
}

#[tauri::command]
pub async fn present(s: St<'_>, talk: String, start: Option<String>) -> Result<(), String> {
    let e = s.engine.clone();
    in_thread(move || e.present(&talk, start.as_deref())).await
}

/// `status`: "approved", "changes" or "clear".
#[tauri::command]
pub async fn review(s: St<'_>, talk: String, name: String, status: String, note: String) -> Result<(), String> {
    check_talk(&talk)?;
    let e = s.engine.clone();
    in_thread(move || {
        let mut args = vec![talk, "note".to_string()];
        match status.as_str() {
            "approved" => args.push("--approve".into()),
            "clear" => args.push("--clear".into()),
            "changes" => {}
            _ => return Err("That review does not exist".into()),
        }
        // After “--” everything is text, even if the note starts with a dash.
        args.extend(["--".into(), name]);
        if !note.trim().is_empty() {
            args.push(note);
        }
        e.text(&args).map(|_| ())
    })
    .await
}

#[tauri::command]
pub fn open_exported(s: St<'_>, talk: String) -> Result<(), String> {
    let pres = s.engine.presentation(&talk).ok_or("There is no such talk")?;
    let folder = pres.join("diapos").join("exported");
    std::fs::create_dir_all(&folder).map_err(|e| e.to_string())?;
    studio_shell::open_folder(&folder)
}
