# SiliconFlow (Text-to-Speech)

import requests
import os
def generate_voice(text, output_path):
    url = "https://api.siliconflow.cn/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {os.getenv('SILICON_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "fishaudio/fish-speech-1.5",
        "input": text,
        "voice": "claire", # Claire is a gentle female voice
        "response_format": "mp3"
    }
    response = requests.post(url, json=payload, headers=headers)
    with open(output_path, "wb") as f:
        f.write(response.content)