from typing import Dict, Any, Optional
from faster_whisper import WhisperModel


def transcribe_audio(
    audio_path: str,
    model_size: str = "small",
    compute_type: Optional[str] = None,
    vad: bool = False,
    no_speech_threshold: float = 0.2,
    log_prob_threshold: float = -2.0,
    compression_ratio_threshold: float = 2.8,
    initial_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Stable, music-friendly transcription using faster-whisper.

    - VAD disabled by default (singing often confuses VAD)
    - Lower no_speech_threshold to avoid early cutoffs
    - Relaxed decoding thresholds for robustness on songs
    - Compatible with older faster-whisper (no unsupported args)

    Returns:
        {
          "segments": [{"start": float, "end": float, "text": str}, ...],
          "duration": float
        }
    """
    model = WhisperModel(model_size, compute_type=compute_type or "auto")

    options = dict(
        vad_filter=vad,
        vad_parameters=dict(min_silence_duration_ms=700) if vad else None,
        word_timestamps=False,            # set True if you want per-word karaoke timing
        beam_size=5,
        best_of=5,
        temperature=0.0,
        compression_ratio_threshold=compression_ratio_threshold,
        log_prob_threshold=log_prob_threshold,
        no_speech_threshold=no_speech_threshold,
        condition_on_previous_text=False, # prevents cascading errors from causing early stop
        initial_prompt=initial_prompt,
    )

    segments_out = []
    total_duration = 0.0

    segments_gen, info = model.transcribe(audio_path, **options)

    for seg in segments_gen:
        text = (seg.text or "").strip()
        if not text:
            continue
        s = float(seg.start or 0.0)
        e = float(seg.end or 0.0)
        segments_out.append({"start": s, "end": e, "text": text})
        if e > total_duration:
            total_duration = e

    return {"segments": segments_out, "duration": total_duration}
