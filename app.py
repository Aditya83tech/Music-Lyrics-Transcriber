import os
import tempfile
import streamlit as st
import pandas as pd

from transcriber.downloader import download_youtube_music
from transcriber.asr import transcribe_audio
from transcriber.utils import (
    segments_to_srt,
    segments_to_lrc,
    segments_to_plaintext,
)

st.set_page_config(page_title="YouTube Music Lyrics Transcriber", page_icon="🎵", layout="centered")

st.title("🎵 YouTube Music Lyrics Transcriber")
st.caption("Accepts ONLY YouTube Music links → downloads audio (yt-dlp) → transcribes with Whisper → exports TXT/SRT/LRC")

with st.expander("⚙️ Settings", expanded=True):
    model_size = st.selectbox(
        "Whisper model (larger = better, slower)",
        ["tiny", "base", "small", "medium", "large-v3"],
        index=2,
    )
    compute_type = st.selectbox(
        "Compute precision",
        ["auto", "int8", "int8_float16", "float16", "float32"],
        index=0,
    )
    # 👇 new: turn VAD off by default (better for songs)
    vad_filter = st.checkbox("Voice activity detection (Silero VAD)", value=False)
    # 👇 new: control the no-speech threshold
    no_speech_threshold = st.slider(
        "No-speech threshold (lower = less likely to stop early)",
        0.0, 1.0, 0.2, 0.05
    )


url = st.text_input(
    "Paste a YouTube Music link:",
    placeholder="https://music.youtube.com/watch?v=VIDEO_ID"
)
go = st.button("Transcribe", type="primary", disabled=not url)

if go:
    # We rely on downloader's strict validation, but add a friendly pre-check too
    if "music.youtube.com/watch" not in url:
        st.error("Only YouTube Music links are allowed (e.g., https://music.youtube.com/watch?v=VIDEO_ID)")
        st.stop()

    # 1) Download audio
    with st.status("🎧 Downloading audio via yt-dlp…", expanded=False) as status:
        try:
            tmp_dir = tempfile.mkdtemp(prefix="ytmusic-lyrics-")
            audio_path, meta = download_youtube_music(url, tmp_dir)
            status.update(label="Audio downloaded ✅", state="complete")
        except Exception as e:
            st.error("Audio download failed.")
            st.exception(e)
            st.stop()

    st.audio(audio_path)

    # 2) Transcribe with Whisper
    with st.status("🧠 Transcribing with faster-whisper…", expanded=False) as status:
        try:
            result = transcribe_audio(
                audio_path=audio_path,
                model_size=model_size,
                compute_type=None if compute_type == "auto" else compute_type,
                vad=vad_filter,
            )
            status.update(label="Transcription complete ✅", state="complete")
        except Exception as e:
            st.error("Transcription failed.")
            st.exception(e)
            st.stop()

    segments = result["segments"]

    # 3) Show results
    st.subheader("Video Info")
    col1, col2 = st.columns(2)
    col1.metric("Title", meta.get("title", "-")[:40])
    col2.metric("Uploader", meta.get("uploader", "-")[:40])

    st.subheader("Transcript")
    full_text = segments_to_plaintext(segments)
    st.text_area("Lyrics (plain text)", value=full_text, height=250)

    df = pd.DataFrame(
        [{"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()} for s in segments]
    )
    st.dataframe(df, use_container_width=True)

    # 4) Downloads
    srt_str = segments_to_srt(segments)
    lrc_str = segments_to_lrc(segments)

    st.subheader("Downloads")
    st.download_button("⬇️ lyrics.txt", data=full_text, file_name="lyrics.txt")
    st.download_button("⬇️ lyrics.srt", data=srt_str, file_name="lyrics.srt")
    st.download_button("⬇️ lyrics.lrc", data=lrc_str, file_name="lyrics.lrc")

st.markdown(
    """
---
**Only YouTube Music links are accepted** (e.g., `https://music.youtube.com/watch?v=VIDEO_ID`).  
Use for personal/educational purposes and respect copyright.
"""
)
