import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = "v21.0" # Latest Meta API version for 2026

BASE_URL = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def send_text(to, text):
    """Sends a standard text message."""
    url = f"{BASE_URL}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def send_audio(to, audio_file_path):
    """Sends an audio file. Note: This requires uploading the media first."""
    # 1. Upload the audio to Meta to get a Media ID
    media_id = upload_media(audio_file_path)
    
    # 2. Send the message using that ID
    url = f"{BASE_URL}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"id": media_id}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def upload_media(file_path):
    """Uploads a file to Meta and returns the Media ID."""
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    headers_upload = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "audio/mpeg"),
        "type": (None, "audio/mpeg"),
        "messaging_product": (None, "whatsapp"),
    }
    
    response = requests.post(url, headers=headers_upload, files=files)
    return response.json().get("id")

def download_media(media_id):
    """Downloads a voice note from Meta's servers using its ID."""
    # Step 1: Get the download URL
    url = f"https://graph.facebook.com/{VERSION}/{media_id}"
    headers_dl = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    res = requests.get(url, headers=headers_dl)
    download_url = res.json().get("url")
    
    # Step 2: Download the actual binary
    media_res = requests.get(download_url, headers=headers_dl)
    
    file_path = f"downloads/{media_id}.ogg"
    os.makedirs("downloads", exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(media_res.content)
        
    return file_path