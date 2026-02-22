from modelo.prompt_llm import build_prompt
from modelo.llm_client import call_llm
from typing import Optional, Dict
import json
import re
from datetime import datetime, timedelta


def _resolve_relative_date(texto: str) -> Optional[str]:
    """
    Resolve 'hoje' e 'ontem' de forma determinística.
    Retorna string no formato YYYY-MM-DD HH:MM ou None.
    """

    texto_lower = texto.lower()
    hora_match = re.search(r'(\d{1,2})h', texto_lower)

    base_date = None

    if "ontem" in texto_lower:
        base_date = datetime.now() - timedelta(days=1)

    elif "hoje" in texto_lower:
        base_date = datetime.now()

    if base_date:
        if hora_match:
            hour = int(hora_match.group(1))
            base_date = base_date.replace(hour=hour, minute=0)
        else:
            base_date = base_date.replace(hour=0, minute=0)

        return base_date.strftime("%Y-%m-%d %H:%M")

    return None


def process_incident(texto: str) -> Dict[str, Optional[str]]:

    # 1️⃣ Resolve data relativa antes do LLM
    data_resolvida = _resolve_relative_date(texto)

    prompt = build_prompt(texto)

    try:
        raw = call_llm(prompt)
    except Exception as e:
        raise Exception(f"Erro ao chamar LLM local: {e}")

    try:
        parsed = json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception as e:
                raise Exception(f"Resposta do LLM não pôde ser convertida em JSON: {e}")
        else:
            raise Exception("Resposta do LLM não contém JSON reconhecível.")

    result = {
        "data_ocorrencia": parsed.get("data_ocorrencia"),
        "local": parsed.get("local"),
        "tipo_incidente": parsed.get("tipo_incidente"),
        "impacto": parsed.get("impacto"),
    }

    # 2️⃣ Se resolvemos hoje/ontem, sobrescreve a data do modelo
    if data_resolvida:
        result["data_ocorrencia"] = data_resolvida

    return result