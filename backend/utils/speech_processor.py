"""
Speech processing module
Converts audio to text using OpenAI Whisper or Google Speech-to-Text
"""

import os
import io

# Support both the older `openai` (0.x) and newer SDKs that expose `OpenAI`
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _use_modern_client = True
except Exception:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    _client = openai
    _use_modern_client = False

def process_audio(audio_file):
    """
    Convert audio to text using OpenAI Whisper
    Args:
        audio_file: Audio file object or path
    Returns:
        Transcribed text
    """
    try:
        # Read bytes from file-like, raw bytes, or path
        if hasattr(audio_file, 'read'):
            audio_bytes = audio_file.read()
        elif isinstance(audio_file, (bytes, bytearray)):
            audio_bytes = bytes(audio_file)
        else:
            with open(audio_file, 'rb') as f:
                audio_bytes = f.read()

        audio_stream = io.BytesIO(audio_bytes)

        if _use_modern_client:
            resp = _client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_stream
            )
            return getattr(resp, 'text', resp.get('text', ''))
        else:
            # older openai package
            resp = _client.Audio.transcribe("whisper-1", audio_stream)
            if hasattr(resp, 'text'):
                return resp.text
            return resp.get('text', '')
    except Exception as e:
        print(f"Error processing audio: {e}")
        return "Error: Could not process audio"

def extract_audio_from_video(video_file):
    """
    Extract audio stream from video file (for WebRTC streams)
    Args:
        video_file: Video file path
    Returns:
        Audio data
    """
    try:
        # Placeholder for video to audio extraction
        # In production, use ffmpeg or similar
        pass
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None
