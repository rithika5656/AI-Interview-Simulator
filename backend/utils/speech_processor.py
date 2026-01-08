"""
Speech processing module
Converts audio to text using OpenAI Whisper or Google Speech-to-Text
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_audio(audio_file):
    """
    Convert audio to text using OpenAI Whisper
    Args:
        audio_file: Audio file object or path
    Returns:
        Transcribed text
    """
    try:
        # If it's a file from request.files
        if hasattr(audio_file, 'read'):
            audio_data = audio_file.read()
        else:
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
        
        # Use OpenAI Whisper API
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_data
        )
        
        return transcript.text
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
