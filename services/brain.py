import os
import requests
import json

HMS_KNOWLEDGE = """
You are 'Ayesha', a professional medical assistant at Sargodha Health HMS.
Knowledge: 
- Labs: We offer CBC, Sugar, Lipid Profile, and PCR tests.
- Pharmacy: Home delivery available in Sargodha.
- Hours: 9 AM to 10 PM.
Rules:
1. If the user mentions a specific test or medicine, they are a [HOT LEAD].
2. If they ask generic questions like 'Price?', ask them 'Which specific test are you looking for?'
3. Output format must be: 
   SCORE: [0-100]
   REPLY: [Your response]
"""

def get_ai_response(user_input: str):
    prompt = f"{HMS_KNOWLEDGE}\n\nUser: {user_input}"
    
    providers = [
        {
            "name": "Gemini",
            "type": "gemini",
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            "body": {
                "contents": [{"parts": [{"text": prompt}]}]
            }
        },
        {
            "name": "Groq",
            "type": "openai",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}", "Content-Type": "application/json"},
            "body": {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}]
            }
        },
        {
            "name": "SiliconFlow",
            "type": "openai",
            "url": "https://api.siliconflow.cn/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {os.getenv('SILICON_API_KEY')}", "Content-Type": "application/json"},
            "body": {
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}]
            }
        }
    ]

    text = ""
    for p in providers:
        try:
            if p["type"] == "gemini":
                response = requests.post(p["url"], json=p["body"], headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    result = response.json()
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"✅ Success with {p['name']}")
                    break
                else:
                    print(f"❌ {p['name']} failed with status {response.status_code}: {response.text}")
                    
            elif p["type"] == "openai":
                response = requests.post(p["url"], json=p["body"], headers=p["headers"])
                if response.status_code == 200:
                    result = response.json()
                    text = result["choices"][0]["message"]["content"]
                    print(f"✅ Success with {p['name']}")
                    break
                else:
                    print(f"❌ {p['name']} failed with status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ {p['name']} error: {e}")
            continue

    if not text:
        return 0, "I apologize, but all our systems are currently down. Please try again later."

    # Parse response
    score = 0
    if "SCORE:" in text:
        try:
            score_str = text.split("SCORE:")[1].split("\n")[0].strip()
            # remove non-digits
            score_str = ''.join(filter(str.isdigit, score_str))
            score = int(score_str) if score_str else 0
        except Exception:
            score = 0
            
    reply = text.split("REPLY:")[1].strip() if "REPLY:" in text else text

    return score, reply