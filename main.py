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


@app.post("/webhook")
async def handle_message(request: Request):
    data =  await request.json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = message['from']
        msg_type = message['type']

        user_input = ""
        is_audio = False

        owner_number = "+923456047058"

        if msg_type == 'text':
            user_input = message['text']['body']
        elif msg_type == 'audio':
            is_audio = True
            audio_id = message['audio']['id']
            path = download_media(audio_id)
            user_input = transcribe_audio(path)

        # Get AI Logic
        score, ai_reply = get_ai_response(user_input)

        # Notify if it's a Hot Lead
        if score > 80:
            send_text(owner_number, f"🔥 HOT LEAD ALERT: {sender} is highly interested!")

        if is_audio:
            voice_path = "reply.mp3"
            generate_voice(ai_reply, voice_path)
            send_audio(sender, voice_path)
        else:
            send_text(sender, ai_reply)

    except Exception as e:
        print(f"Error: {e}")

    return {"status": "ok"}