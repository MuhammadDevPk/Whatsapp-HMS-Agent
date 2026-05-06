# Meta API (Send/Receive/Download)

import uuid
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = "v21.0"

BASE_URL = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def send_text(to, text):
    """
    Sends a standard text message to a specific WhatsApp number.
    """
    url = f"{BASE_URL}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    # Added timeout=10
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    return response.json()

def send_audio(to, audio_file_path):
    """
    Uploads and sends an audio file/voice note to a user.
    """
    media_id = upload_media(audio_file_path)

    url = f"{BASE_URL}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"id": media_id}
    }
    # Added timeout=10
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    return response.json()

def upload_media(file_path):
    """
    Uploads a local file to Meta's media servers and returns the media ID.
    """
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    headers_upload = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "audio/mpeg"),
        "type": (None, "audio/mpeg"),
        "messaging_product": (None, "whatsapp"),
    }

    # Increased timeout to 20 for uploads
    response = requests.post(url, headers=headers_upload, files=files, timeout=20)
    return response.json().get("id")

def download_media(media_id):
    """
    Retrieves the download URL for a media ID and saves it to the local downloads folder.
    """
    url = f"https://graph.facebook.com/{VERSION}/{media_id}"
    headers_dl = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # Added timeout=10
    res = requests.get(url, headers=headers_dl, timeout=10)
    download_url = res.json().get("url")

    unique_name = f"{uuid.uuid4()}.ogg" # Unique ID

    # Added timeout=30 (Voice notes can be large sometimes)
    media_res = requests.get(download_url, headers=headers_dl, timeout=30)
    file_path = f"downloads/{unique_name}"
    os.makedirs("downloads", exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(media_res.content)

    return file_path