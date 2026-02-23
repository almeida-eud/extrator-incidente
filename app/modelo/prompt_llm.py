def construir_prompt(texto: str) -> str:
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
  Cidade mencionada no texto.
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