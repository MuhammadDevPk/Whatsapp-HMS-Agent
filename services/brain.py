# Gemini Lead Qualification

import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"{HMS_KNOWLEDGE}\n\nUser: {user_input}")

    # Simple parsing to separate score from text
    text = response.text
    score = 0

    if "SCORE:" in text:
        score = int(text.split("SCORE:")[1].split("\n")[0].strip())
    reply = text.split("REPLY:")[1].strip() if "REPLY:" in text else text

    return score, reply