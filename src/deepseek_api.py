import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_code(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "あなたはプロのプログラマーとして、明確で安全なコードを出力します。"},
            {"role": "user", "content": f"{prompt}"}
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    res = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=30)
    if res.status_code != 200:
        return f"APIエラー: {res.status_code}\n{res.text}"

    return res.json()["choices"][0]["message"]["content"]
