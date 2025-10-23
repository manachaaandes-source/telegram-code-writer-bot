import requests
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENROUTER_API_KEY_2 = os.getenv("OPENROUTER_API_KEY_2")

def call_model(prompt, model, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://example.com",
        "X-Title": "CodeWriterBot"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }
    return requests.post(url, headers=headers, json=data, timeout=60)

def generate_code(prompt, length="medium", lang="Python"):
    length_tokens = {"short": 400, "medium": 900, "long": 1500}.get(length, 900)
    full_prompt = f"言語: {lang}\nコード長: {length}\n\n{prompt}"

    res = call_model(full_prompt, "deepseek/deepseek-chat-v3.1:free", DEEPSEEK_API_KEY)
    if res.status_code == 200:
        try:
            return res.json()["choices"][0]["message"]["content"]
        except:
            pass

    print("⚠️ DeepSeek失敗:", res.status_code, res.text)
    res2 = call_model(full_prompt, "openai/o4-mini-deep-research", OPENROUTER_API_KEY_2)
    if res2.status_code == 200:
        return "(Fallback: openai/o4-mini)\n\n" + res2.json()["choices"][0]["message"]["content"]
    return f"❌ APIエラー\nDeepSeek: {res.status_code}\nOpenAI: {res2.status_code}"
