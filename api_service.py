import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_ai_response(user_message, conversation_history=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://adika.app",
        "X-Title": "Adika Financial Advisor"
    }

    SYSTEM_PROMPT = """You are Adika's Senior Financial Advisor in Ethiopia.

STRICT EXECUTION RULES:
1. LANGUAGE: Respond EXCLUSIVELY in natural, clean, professional Amharic (ንጹህ እና ተፈጥሮአዊ አማርኛ). Never output foreign scripts or mixed English terms.
2. NO RAW MARKDOWN: Do NOT output formatting symbols like **, *, or ###. Output plain structured text with numbered lists (1, 2, 3) only.
3. FINANCIAL DATA ACCURACY: Never state fixed bank interest rates or false car prices. Explain that loan rates in Ethiopia float (~16%-24%+) and advise contacting bank branches directly.
4. CONVERSATIONAL TONE: Be direct, helpful, warm, and natural like a human expert in Addis Ababa."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if conversation_history:
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
            
    messages.append({"role": "user", "content": user_message})

    # DeepSeek-V3 OpenRouter Payload
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": messages,
        "temperature": 0.3,
        "repetition_penalty": 1.2,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        
        # Log response status to server console for debugging
        print(f"DeepSeek API Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"DeepSeek API Error Body: {response.text}")
            return "ይቅርታ፣ ከሲስተሙ ጋር መገናኘት አልተቻለም። እባክዎን የኢንተርኔት ግንኙነትዎን አረጋግጠው ደግመው ይሞክሩ።"

        data = response.json()
        raw_output = data['choices'][0]['message']['content']

        # Clean residual markdown symbols
        clean_text = raw_output.replace('**', '').replace('*', '').replace('###', '').strip()
        return clean_text

    except Exception as e:
        print(f"DeepSeek API Exception: {str(e)}")
        return "ይቅርታ፣ አሁን ላይ አገልግሎቱን ማቅረብ አልተቻለም። እባክዎን ትንሽ ቆይተው እንደገና ይሞክሩ።"
