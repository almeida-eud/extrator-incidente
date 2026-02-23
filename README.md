# Extrator de Incidentes — README

Projeto: Extrator de Incidentes Corporativos

Este repositório contém uma API em FastAPI (GET e POST) que recebe textos, envia um prompt para um LLM local (via Ollama) para extrair campos estruturados sobre um incidente e retorna um JSON com os campos:

```json
{
  "data_ocorrencia": "...",
  "local": "...",
  "tipo_incidente": "...",
  "impacto": "..."
}
```

Observação: o endpoint GET armazena em memória o último texto recebido; o POST usa o texto enviado no body ou, se não houver body, usa o último texto armazenado pelo GET.


------------------------------------------------------------------------

# Sumário

-   Visão Geral
-   Requisitos
-   Estrutura do Projeto
-   Configuração
-   Execução Local (sem Docker)
-   Execução com Docker
-   Endpoints da API
-   Solução de Problemas
-   Boas Práticas

------------------------------------------------------------------------

# Visão Geral

O sistema funciona da seguinte forma:

1.  Recebe texto via endpoint HTTP.
2.  Normaliza o texto.
3.  Constrói um prompt estruturado.
4.  Envia o prompt para um modelo LLM local.
5.  Processa a resposta e retorna um JSON validado.

A API exige autenticação via chave (`API_KEY`) enviada no header
`senha`.

------------------------------------------------------------------------

# Requisitos

Ambiente mínimo recomendado:

-   Git (para clonar o repositório)
-   Python 3.11 (ou 3.10 compatível)
-   pip
-   Ambiente virtual (venv)
-   Docker (opcional)
-   Ollama em execução local

Sistema testado: Windows (WSL/Ubuntu-22.04).

Observação: Se usar o LLM local: Ollama (ou outro endpoint compatível). Por padrão o cliente espera http://localhost:11434/api/generate.
------------------------------------------------------------------------

# Estrutura do Projeto

EXTRATOR-INCIDENTE/
│
├── app/
│   ├── api/
│   │   └── incidente_endpoints.py
│   │
│   ├── modelo/
│   │   ├── llm_client.py
│   │   └── prompt_llm.py
│   │
│   ├── pre_processamento/
│   │   ├── processamento.py
│   │   └── schema.py
│   │
│   ├── service/
│   │   └── incidente_service.py
│   │
│   ├── .env
│   ├── main.py
│   └── requirements.txt
│
├── .dockerignore
├── .gitignore
├── Dockerfile
└── README.md
------------------------------------------------------------------------

# Configuração

Crie um arquivo `.env` na pasta app/ do projeto com o seguinte conteúdo:

API_KEY=12A3
Observação: **Para fins do teste**, a senha foi adicionada acima.

Descrição das variáveis:

-   `API_KEY`: chave obrigatória para autenticar chamadas à API.

Nunca versionar o arquivo `.env`.

------------------------------------------------------------------------

# Instalação do modelo LLM Ollama (llama3.2:1b)

Também será necessário instalar o modelo LLM (llama3.2:1b) que é utilizado neste projeto. Esse modelo funciona localmente.

No Terminal:

- Instalar o Ollama
curl -fsSL https://ollama.com/install.sh | sh

- Iniciar o serviço Ollama
ollama serve

- Baixar o modelo utilizado neste projeto
ollama pull llama3.2:1b

------------------------------------------------------------------------

# Execução Local (sem Docker)

1.  Criar ambiente virtual:

Observação: Certificar que está em ambiente Linux, se for Windows, WSL:Ubuntu-22.04.

Terminal/WSL:Ubuntu-22.04: python -m venv extrator-incidente

Apois a instalação, ative o ambiente:

Terminal/WSL:Ubuntu-22.04: source bin/activate

2.  Instalar dependências:

pip install -r requirements.txt

3.  Executar aplicação:

Terminal/WSL:Ubuntu-22.04: python main.py

Observação: É necessário estar na pasta app/

Acesse para ver os Endpoints da API:

http://localhost:8000/docs

------------------------------------------------------------------------

# Execução com Docker

Build da imagem:

docker build -t extrator-incidente .

Executar container:

docker run --rm -p 8000:8000 --env-file .env extrator-incidente

Acesse:

http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# Endpoints da API

## GET /extract

Armazena o texto normalizado em memória.

Exemplo:

curl -X GET "http://127.0.0.1:8000/extract?texto=Houve queda de energia
hoje às 14h" -H "senha: SUA_API_KEY"

------------------------------------------------------------------------

## POST /extract

Processa o texto e retorna JSON estruturado.

Exemplo:

curl -X POST "http://127.0.0.1:8000/extract" -H "Content-Type:
application/json" -H "senha: SUA_API_KEY" -d '{"texto": "Hoje houve
instabilidade de rede em Belém das 09h às 10h"}'

Resposta esperada:

{ "data_ocorrencia": "2026-02-23 09:00", "local": "Belem",
"tipo_incidente": "Instabilidade de rede", "impacto": "Usuários sem
acesso por 1 hora" }

------------------------------------------------------------------------

# Solução de Problemas

Erro 401 -- API key inválida - Verifique se o header `senha` está sendo
enviado corretamente.

Erro ao chamar LLM - Confirme se o Ollama está rodando. - Verifique se a
variável `OLLAMA_URL` está correta.

Porta já em uso - Mude a porta do Uvicorn ou do Docker.

------------------------------------------------------------------------

# Boas Práticas

-   Utilize chave forte para `API_KEY`.
-   Não exponha o serviço LLM diretamente.
-   Utilize HTTPS em ambiente de produção.
-   Restrinja acesso via firewall quando necessário.
-   Monitore logs em ambiente produtivo.

------------------------------------------------------------------------

# Licença

Definir licença do projeto (ex: MIT, Apache 2.0).
