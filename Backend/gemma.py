import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def ask_gemma(prompt: str) -> str:
    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        res.raise_for_status()
        return res.json()["response"]

    except Exception as e:
        return f"[Gemma Error]: {e}"