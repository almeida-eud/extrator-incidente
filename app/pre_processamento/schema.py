from pydantic import BaseModel
from typing import Optional

class RespostaIncidente(BaseModel):
    """
    Função para padronizar a resposta da API.
    """
    data_ocorrencia: Optional[str]
    local: Optional[str]
    tipo_incidente: Optional[str]
    impacto: Optional[str]