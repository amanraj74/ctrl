import os

import requests
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/models"
headers = {
    "Authorization": f"Bearer {groq_api_key}",
    "Content-Type": "application/json"
}

url_chat = "https://api.groq.com/openai/v1/chat/completions"
for model in ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "allam-2-7b"]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    r = requests.post(url_chat, headers=headers, json=payload)
    if r.status_code == 200:
        print(f"{model} SUCCESS: {r.json()['choices'][0]['message']['content']}")
    else:
        print(f"{model} FAILED: {r.status_code} {r.text}")
