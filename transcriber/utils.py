from typing import List, Dict

def _format_ts_srt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def _format_ts_lrc(t: float) -> str:
    m = int(t // 60)
    s = int(t % 60)
    cs = int(round((t - int(t)) * 100))
    return f"[{m:02d}:{s:02d}.{cs:02d}]"

def segments_to_plaintext(segments: List[Dict]) -> str:
    return "\n".join(seg["text"].strip() for seg in segments if seg.get("text"))

def segments_to_srt(segments: List[Dict]) -> str:
    lines = []
    idx = 1
    for seg in segments:
        if not seg.get("text"): continue
        lines.append(f"{idx}\n{_format_ts_srt(seg['start'])} --> {_format_ts_srt(seg['end'])}\n{seg['text'].strip()}\n")
        idx += 1
    return "\n".join(lines).strip() + "\n"

def segments_to_lrc(segments: List[Dict]) -> str:
    return "\n".join(f"{_format_ts_lrc(seg['start'])}{seg['text'].strip()}" for seg in segments if seg.get("text")) + "\n"
