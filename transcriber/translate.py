# transcriber/translate.py
from typing import Optional
from langdetect import detect
from transformers import MarianMTModel, MarianTokenizer

_cache = {}

def _get_model(src, tgt):
    key = f"{src}-{tgt}"
    if key in _cache:
        return _cache[key]
    model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
    tok = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    _cache[key] = (tok, model)
    return _cache[key]

def translate_text(text: str, target_lang: str = "en") -> str:
    try:
        src_lang = detect(text)
    except Exception:
        src_lang = "en"
    if src_lang.startswith(target_lang):
        return text
    tok, model = _get_model(src_lang, target_lang)
    batch = tok.prepare_seq2seq_batch([text], return_tensors="pt")
    translated = model.generate(**batch)
    return tok.decode(translated[0], skip_special_tokens=True)
