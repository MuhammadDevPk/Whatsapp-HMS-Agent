from fastapi import FastAPI, Request, Response
from services.whatsapp import send_text, send_audio, download_media
from services.stt import transcribe_audio
from services.brain import get_ai_response
from services.tts import generate_voice
import os

app = FastAPI()

@app.get("/webhook") #For Whatsapp verification
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return Response(content=params.get("hub.challenge"))
    return "Verification Failed"