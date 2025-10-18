# 🎵 YouTube Music Lyrics Transcriber (Streamlit + Whisper)

A simple Streamlit app that  
1️⃣ takes a **YouTube Music** link,  
2️⃣ downloads its audio with **yt-dlp** using `ffmpeg`, and  
3️⃣ transcribes the full song into text with **OpenAI Whisper** (via `faster-whisper`).  

Outputs ready-to-download **TXT**, **SRT**, and **LRC** lyric files.

---

## ✨ Features
- Paste a `https://music.youtube.com/watch?v=…` link  
- Full-length audio download (no previews)  
- Local, completely **free** Whisper transcription  
- Adjustable model size & precision  
- Music-friendly decoding (no VAD by default, low no-speech threshold)  
- Export `.txt`, `.srt`, `.lrc`  


---

## 🧰 Requirements
- **Python 3.9 or newer**
- **ffmpeg** (must be installed and on PATH)  
  - 🪟 Windows → download [from gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract to `C:\ffmpeg`, add `C:\ffmpeg\bin` to PATH  
  - 🍎 macOS → `brew install ffmpeg`  
  - 🐧 Linux → `sudo apt install ffmpeg`
- Recommended GPU (>= 4 GB VRAM) but works on CPU

---

## 📦 Installation
```bash
git clone https://github.com/yourname/youtube-lyrics-transcriber.git
cd youtube-lyrics-transcriber

python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
