from fastapi import FastAPI, Request, Response, BackgroundTasks
from services.whatsapp import send_text, send_audio, download_media
from services.stt import transcribe_audio
from services.brain import get_ai_response
from services.tts import generate_voice
import uuid
import os

app = FastAPI()

@app.get("/")
async def home():
    return {"status": "HMS Agent is Online"}


@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return Response(content=params.get("hub.challenge"))
    return "Verification Failed"


def process_agent_logic(data: dict):
    """The heavy lifting happens here, away from the main request."""
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = message['from']
        msg_type = message['type']
        
        user_input = ""
        is_audio = False

        if msg_type == 'text':
            user_input = message['text']['body']
        elif msg_type == 'audio':
            is_audio = True
            audio_id = message['audio']['id']
            path = download_media(audio_id)
            user_input = transcribe_audio(path)
            os.remove(path) # Clean up original audio

        # AI Thought Process
        score, ai_reply = get_ai_response(user_input)

        # Notify if it's a Hot Lead
        if score > 80:
            owner_number = "+923456047058"
            send_text(owner_number, f"🔥 HOT LEAD ALERT: {sender} is highly interested!")

        if is_audio:
            unique_voice_path = f"downloads/{uuid.uuid4()}.mp3"
            generate_voice(ai_reply, unique_voice_path)
            send_audio(sender, unique_voice_path)
            os.remove(unique_voice_path) # Clean up generated audio
        else:
            send_text(sender, ai_reply)
            
    except Exception as e:
        print(f"Background Process Error: {e}")

@app.post("/webhook")
async def handle_message(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # 1. Immediately tell Meta we received the message
    # This prevents WhatsApp from sending the same message 5 times
    background_tasks.add_task(process_agent_logic, data)
    
    return Response(content="Accepted", status_code=202)