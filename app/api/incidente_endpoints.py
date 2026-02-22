from fastapi import FastAPI, HTTPException, Query, Body, Depends, Header
from pre_processamento.processamento import normalize_text
from pre_processamento.schema import IncidentResponse
from modelo.prompt_llm import build_prompt
from typing import Optional, Dict, Any
from modelo.llm_client import call_llm
from dotenv import load_dotenv
import pandas as pd
from threading import Lock
import json
import re
import os


app = FastAPI(title="API de Extrator de Incidente")


# Senha para utilizar os endpoints
load_dotenv()
API_KEY = os.getenv("API_KEY")

def verify_api_key(senha: str = Header(...)):
    if senha != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")


# armazenamento simples em memória para o último texto recebido via GET
_LAST_TEXT: Optional[str] = None
_LOCK = Lock()


@app.get("/extract", 
         dependencies=[Depends(verify_api_key)])
def extract_get(texto: Optional[str] = Query(None, description="Descrição do incidente")):
    """
    Recebe o texto via query string 'texto' e armazena como último texto recebido.
    Ex.: GET /extract?texto=Ontem+às+14h...
    """
    if not texto:
        raise HTTPException(status_code=400, detail="Parâmetro 'texto' é obrigatório " \
        "no GET para armazenar o texto.")

    texto_norm = normalize_text(texto)

    with _LOCK:
        global _LAST_TEXT
        _LAST_TEXT = texto_norm

    return {"status": "received", 
            "texto": texto_norm}


@app.post("/extract", 
          response_model=IncidentResponse, 
          dependencies=[Depends(verify_api_key)])
def extract_post(payload: Optional[Dict[str, Any]] = Body(None)):
    """
    Processa o texto e retorna o JSON estruturado.
    - Se o body JSON contiver {"texto": "..."} usa esse texto.
    - Caso contrário usa o último texto recebido via GET.
    """
    # obtém texto do body (se houver)
    texto_body: Optional[str] = None
    if payload and isinstance(payload, dict):
        texto_body = payload.get("texto")

    if texto_body:
        texto = normalize_text(texto_body)
    else:
        with _LOCK:
            texto = _LAST_TEXT

    if not texto:
        raise HTTPException(status_code=400, detail="Nenhum texto disponível. " \
        "Envie via GET /extract?texto=... ou POST {'texto': '...'}.")

    prompt = build_prompt(texto)

    try:
        raw = call_llm(prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao chamar LLM local: {e}")

    # tenta converter a resposta em JSON: primeiro parse direto, senão extrai bloco JSON das chaves
    parsed: Dict[str, Optional[str]]
    try:
        parsed = json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Resposta do LLM não pôde ser convertida em JSON: {e}")
        else:
            raise HTTPException(status_code=500, detail="Resposta do LLM não contém JSON reconhecível.")

    # normaliza/garante apenas os campos esperados
    result = {
        "data_ocorrencia": parsed.get("data_ocorrencia"),
        "local": parsed.get("local"),
        "tipo_incidente": parsed.get("tipo_incidente"),
        "impacto": parsed.get("impacto"),
    }

    return result