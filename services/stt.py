# Groq Whisper (Speech-to-Text)

from groq import Groq
import os

def transcribe_audio(file_path):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model = "whisper-large-v3-turbo",
            response_format = "text",
        )
    return transcription
