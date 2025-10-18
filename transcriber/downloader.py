import json
import subprocess
from pathlib import Path
from typing import Tuple, Dict
from urllib.parse import urlparse, parse_qs


def _ensure_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except Exception:
        raise RuntimeError("ffmpeg not found. Install it and make sure it's on PATH.")


def _validate_and_get_video_id(url: str) -> str:
    """
    Accept ONLY YouTube Music watch links:
      https://music.youtube.com/watch?v=VIDEO_ID
    """
    u = urlparse(url.strip())
    if u.netloc.lower() != "music.youtube.com":
        raise ValueError("Only links from music.youtube.com are allowed.")
    if u.path != "/watch":
        raise ValueError("Only watch links are supported.")
    q = parse_qs(u.query)
    vid = q.get("v", [None])[0]
    if not vid:
        raise ValueError("Missing ?v=VIDEO_ID in the link.")
    return vid


def download_youtube_music(url: str, out_dir: str) -> Tuple[str, Dict]:
    """
    Downloads audio from a YouTube Music link using yt-dlp.
    Returns (audio_path, metadata)
    """
    video_id = _validate_and_get_video_id(url)
    _ensure_ffmpeg()

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    out_file = out / "%(title)s.%(ext)s"

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--no-playlist",
        "--write-info-json",
        "-o", str(out_file),
        url,
    ]

    res = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode != 0:
        raise RuntimeError(f"yt-dlp failed to download audio.\n\n{res.stdout}")

    mp3_files = sorted(out.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp3_files:
        raise RuntimeError("yt-dlp finished but no .mp3 file was found.")

    audio_path = str(mp3_files[0])
    info_files = sorted(out.glob("*.info.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    meta = {"title": Path(audio_path).stem, "uploader": "-"}
    if info_files:
        with open(info_files[0], "r", encoding="utf-8") as f:
            info = json.load(f)
        meta["title"] = info.get("title", meta["title"])
        meta["uploader"] = info.get("uploader", "-")

    return audio_path, meta
