from fastapi import FastAPI, HTTPException, Query, Body
from typing import Optional, Dict, Any
import json
import re
from threading import Lock

from pre_processamento.schema import IncidentResponse
from pre_processamento.processamento import normalize_text
from modelo.llm_client import call_llm

app = FastAPI(title="API de Extrator de Incidente")

# armazenamento simples em memória para o último texto recebido via GET
_LAST_TEXT: Optional[str] = None
_LOCK = Lock()

def build_inline_prompt(texto: str) -> str:
    return f"""
Você é um sistema de extração estruturada de incidentes corporativos.

Sua tarefa é extrair informações objetivas do texto.
Responda SOMENTE com JSON válido.
Não escreva explicações, comentários ou texto fora do JSON.

Definições IMPORTANTES:

- data_ocorrencia:

Regras obrigatórias:

1. O formato final deve ser exatamente:
   YYYY-MM-DD HH:MM

2. Se o texto contiver:
   - "hoje" → use DATA ATUAL DO SISTEMA
   - "ontem" → subtraia 1 dia da DATA ATUAL DO SISTEMA
   - "anteontem" → subtraia 2 dias

3. Se houver apenas hora (ex: "às 14h"):
   - Combine com a data resolvida acima.
   - Se não houver referência de dia, use null.

4. Se houver data explícita (ex: 05/10/2023 ou 2023-10-05):
   - Converta obrigatoriamente para formato YYYY-MM-DD
   - Se houver hora, inclua HH:MM
   - Se não houver hora, use 00:00

5. Nunca retorne datas em outro formato.
6. Nunca retorne texto fora do JSON.


- local:
  Cidade, unidade, escritório ou local mencionado no texto.
  Não invente informação.

- tipo_incidente:
  Classifique o evento principal em uma categoria curta e objetiva.
  Use descrições como:
    "Queda de energia"
    "Instabilidade de rede"
    "Erro no banco de dados"
    "Falha em sistema"
    "Problema em equipamento"
  NÃO descreva o impacto aqui.
  NÃO escreva frases longas.
  Deve ser uma classificação resumida do problema técnico.

- impacto:
  Descreva de forma breve o efeito causado pelo incidente.
  Foque no que foi afetado e por quanto tempo.
  Exemplo:
    "Usuários impedidos de acessar a rede por 1 hora"
    "Processamento de pedidos interrompido por 3 horas"
    "Sistema de faturamento indisponível por duas horas"
  NÃO repita o tipo do incidente.
  Foque na consequência.

Regras:
- Não invente informações.
- Se um campo não estiver claro, use null.
- Sempre retorne todas as chaves.

Formato obrigatório:

{{
  "data_ocorrencia": "...",
  "local": "...",
  "tipo_incidente": "...",
  "impacto": "..."
}}

Texto:
\"\"\"{texto}\"\"\"
"""

@app.get("/extract")
def extract_get(texto: Optional[str] = Query(None, description="Descrição do incidente")):
    """
    Recebe o texto via query string 'texto' e armazena como último texto recebido.
    Ex.: GET /extract?texto=Ontem+às+14h...
    """
    if not texto:
        raise HTTPException(status_code=400, detail="Parâmetro 'texto' é obrigatório no GET para armazenar o texto.")

    texto_norm = normalize_text(texto)

    with _LOCK:
        global _LAST_TEXT
        _LAST_TEXT = texto_norm

    return {"status": "received", "texto": texto_norm}

@app.post("/extract", response_model=IncidentResponse)
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
        raise HTTPException(status_code=400, detail="Nenhum texto disponível. Envie via GET /extract?texto=... ou POST {'texto': '...'}.")

    prompt = build_inline_prompt(texto)

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