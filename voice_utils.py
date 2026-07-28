"""
voice_utils.py

Handles turning Ava's text replies into spoken audio, so the assistant can
talk back to the customer instead of only showing text. Speech-to-text is
not handled here, since recorded customer audio is sent directly to Gemini
for transcription in gemini_client.transcribe_audio, which keeps the
pipeline simple and avoids extra dependencies.
"""

import io
from gtts import gTTS


def text_to_speech(text: str, lang: str = "en") -> bytes:
    """
    Convert text into MP3 audio bytes using gTTS, so it can be played back
    in the Streamlit interface with st.audio.
    """
    clean_text = text.strip()
    if not clean_text:
        return b""

    buffer = io.BytesIO()
    tts = gTTS(text=clean_text, lang=lang)
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()
