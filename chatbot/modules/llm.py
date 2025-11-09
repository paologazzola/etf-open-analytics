# modules/llm.py — Use external Ollama over HTTP (CPU-only fine)
import os
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("LLM_MODEL_NAME", "llama3.1:8b-instruct-q4_K_M")

def chat_completion(prompt: str, system: str | None = None,
                    temperature: float = 0.2, top_p: float = 0.9) -> str:
    """Send a chat completion request to the external Ollama server (non-streaming)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    r = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": MODEL,
            "messages": messages,
            "options": {"temperature": temperature, "top_p": top_p},
            "stream": False,  # <<< IMPORTANT: get a single JSON object (not NDJSON)
        },
        timeout=600,
    )
    r.raise_for_status()
    data = r.json()
    return data["message"]["content"].strip()
