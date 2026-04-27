from fastapi import FastAPI, Request, Response
from services.whatsapp import send_text, send_audio, download_media
from services.stt import transcribe_audio
from services.brain import get_ai_response
from services.tts import generate_voice
import os

