import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"  # ajuste conforme modelo disponível localmente

def call_llm(prompt: str) -> str:
    """
    Chama o Ollama local e retorna o texto bruto da resposta.
    Lança requests.HTTPError em caso de falha.
    """
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 512,
                "top_p": 0.9
        }
        },
        timeout=620
    )
    resp.raise_for_status()
    data = resp.json()
    # dependendo da versão do Ollama a chave pode variar; ajustar se necessário
    # aqui assumimos que a resposta em texto vem em data["response"]
    return data.get("response") or data.get("text") or ""