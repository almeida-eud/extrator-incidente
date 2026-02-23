from fastapi import FastAPI, HTTPException, Query, Body, Depends, Header
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from threading import Lock
import os

from pre_processamento.processamento import normalizar_texto
from pre_processamento.schema import RespostaIncidente
from service.incidente_service import processar_incidente


app = FastAPI(title="API de Extrator de Incidente")

# Senha para utilizar os endpoints
load_dotenv()
API_KEY = os.getenv("API_KEY")

def verificar_api_key(senha: str = Header(...)):
    if senha != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")

# armazenamento simples em memória para o último texto recebido via GET
_LAST_TEXT: Optional[str] = None
_LOCK = Lock()


@app.get("/extract",
         dependencies=[Depends(verificar_api_key)])
def enviar_descricao(texto: Optional[str] = Query(None, description="Descrição do incidente")):
    """
    Endpont para enviar a descrição do incidente.
    """

    if not texto:
        raise HTTPException(
            status_code=400,
            detail="Parâmetro 'texto' é obrigatório no GET para armazenar o texto."
        )

    texto_norm = normalizar_texto(texto)

    with _LOCK:
        global _LAST_TEXT
        _LAST_TEXT = texto_norm

    return {"status": "received", "texto": texto_norm}


@app.post("/extract",
          response_model=RespostaIncidente,
          dependencies=[Depends(verificar_api_key)])
def processar_descricao(payload: Optional[Dict[str, Any]] = Body(None)):
    """
    Endpont para processar a descrição do incidente.
    """

    texto_body: Optional[str] = None
    if payload and isinstance(payload, dict):
        texto_body = payload.get("texto")

    if texto_body:
        texto = normalizar_texto(texto_body)
    else:
        with _LOCK:
            texto = _LAST_TEXT

    if not texto:
        raise HTTPException(
            status_code=400,
            detail="Nenhum texto disponível. Envie via GET ou POST."
        )

    try:
        result = processar_incidente(texto)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result