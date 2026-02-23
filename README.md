# Extrator de Incidentes

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

**Observação**: o endpoint GET armazena em memória o último texto recebido; o POST usa o texto enviado no body ou, se não houver body, usa o último texto armazenado pelo GET.


------------------------------------------------------------------------

# Sumário

-   Visão Geral
-   Requisitos
-   Clonando o Projeto
-   Estrutura do Projeto
-   Configuração
-   Estrutura do Projeto
-   Instalação do modelo LLM Ollama
-   Execução Local (sem Docker)
-   Execução com Docker
-   Endpoints da API
-   Evoluções Futuras

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

**Observação**: Se usar o LLM local: Ollama. Por padrão o cliente espera http://localhost:11434/api/generate.

------------------------------------------------------------------------

# Clonando o Projeto

1. Baixe o projeto para o seu diretório

- Link do projeto no Github:
https://github.com/almeida-eud/extrator-incidente

------------------------------------------------------------------------

# Configuração (Adicionando o arquivo .env)

1. **Crie um arquivo `.env` na pasta app/** do projeto com o seguinte conteúdo:

API_KEY=12A3

**Observação**: **Para fins do teste**, a senha foi adicionada acima.

Descrição da variável:

-   `API_KEY`: chave obrigatória para autenticar chamadas à API.

Nunca versionar o arquivo `.env`.

------------------------------------------------------------------------

# Estrutura do Projeto

```text 
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
```

------------------------------------------------------------------------

# Instalação do modelo LLM Ollama (llama3.2:1b)

**Observação**: Certificar que está em ambiente Linux, se for Windows, WSL:Ubuntu-22.04.

Também será necessário instalar o modelo LLM (llama3.2:1b) que é utilizado neste projeto. Esse modelo funciona localmente.

No Terminal/WSL:Ubuntu-22.04:

- Instalar o Ollama:

`curl -fsSL https://ollama.com/install.sh | sh`

- Iniciar o serviço Ollama:

`ollama serve`

- Baixar o modelo utilizado neste projeto

`ollama pull llama3.2:1b`

------------------------------------------------------------------------

# Execução Local (sem Docker)

**Criar ambiente virtual**:

**Observação**: Certificar que está em ambiente Linux, se for Windows, WSL:Ubuntu-22.04.

No Terminal/WSL:Ubuntu-22.04:

1. **Instalar o ambiente de desenvolvimento**

 `python3.11 -m venv extrator-incidente`

Apois a instalação, ative o ambiente:

 `source extrator-incidente/bin/activate`

2.  **Instalar dependências**:

**Observação**: Para executar o requirements.txt é necessário estar na pasta app/

 `pip install -r requirements.txt`

3.  **Executar aplicação**:

**Observação**: Para executar o main.py é necessário estar na pasta app/

 `python main.py`

Acesse para ver a API:

http://localhost:8000/docs

------------------------------------------------------------------------

# Execução com Docker

Certifique que o docker está instalado adequadamente.

Abra o prompt de comando, vá até a raiz onde baixou o projeto, e irá encontrar o arquivo Dockerfile.

- No prompt, digite o comando para Build da imagem:

`docker build -t extrator-incidente .`

- No prompt, digite o comando para Executar container:

`docker run -p 8000:8000 --env-file app/.env -e OLLAMA_URL=http://host.docker.internal:11434/api/generate -e API_KEY=12A3 extrator-incidente`

**Observação**: Quando a aplicação é utilizada no terminal python usamos OLLAMA_URL=http://localhost:11434/api/generate (llm_client.py), mas quando vamos rodar o container precisamos mudar para OLLAMA_URL=http://host.docker.internal:11434/api/generate extrator-incidente, pois o modelo não é instalado junto com a imagem, então temos que usar o modelo local. Também precisa adicionar a senha da API (API_KEY=12A3), caso não tenha retirado o .env do diretório.

Acesse para ver a API:

http://localhost:8000/docs

------------------------------------------------------------------------

# Endpoints da API

- GET

Endpont para enviar a descrição do incidente.

É necessário preencher dois campos:
texto: Descrição do incidente.
senha: Senha para utilizar o endpoint.

Após preencher os campos é só executar.

Resposta esperada:

```json
{
  "status": "received",
  "texto": "ontem as 14h, no escritorio de sao paulo, houve uma falha no servidor principal que afetou o sistema de faturamento por 2 horas."
}
```

- POST

Endpont para processar a descrição do incidente e retorna JSON estruturado.

É necessário preencher um campo:

senha: Senha para utilizar o endpoint.

Após preencher o campo é só executar.

Resposta esperada:

```json
{
  "data_ocorrencia": "2026-02-22 14:00",
  "local": "Sao Paulo",
  "tipo_incidente": "Falha em sistema",
  "impacto": "Usuários impedidos de acessar a rede por 2 horas"
}
```
------------------------------------------------------------------------

# Solução de Problemas

Erro 401 -- API key inválida - Verifique se o header `senha` está sendo
enviado corretamente.

Erro ao chamar LLM - Confirme se o Ollama está rodando. - Verifique se a
variável `OLLAMA_URL` está correta.

Porta já em uso - Mude a porta do Uvicorn ou do Docker.

------------------------------------------------------------------------

# Evoluções Futuras

1. Melhorar a segurança dos Endpoints

No teste foi utilizado uma senha simples, mas em produção o ideal é usar soluções mais robustas como JWT ou OAuth

2. Percistência dos dados

Utilizei somente um armazenamento em memória neste teste. Mas o ideal é termos um banco de dados (ex: postgres) para deixar os dados estruturados, além de termos uma garantia para que se a API cair ainda teremos os dados salvos em banco. O que também ajuda a ter uma base de dados maior pensando no retraining

3. Testes Automatizados

Fazer alguns testes, como:

- Unitários (pytest)
- Testes de API

4. Monitoramento

Monitoramento de algumas métrica, como:

- Latência média
- Taxa de erro
- Mudança no padrão textual
- Uso de CPU / RAM (LLM consome muita memória)

5. Retraining / Evolução do Modelo

Criar um pipeline de retraining com:

- Coleta de exemplos errados automaticamente
- Armazenar em dataset incremental
- Re-treinar periodicamente

6. Escalabilida

O ideal, antes de começar a criar o projeto, seria estimar quantas requisições teremos por minuto. Somente conectar a API diretamente ao LLM provavelmente não será suficiente para suportar carga, pois o LLM é um componente pesado e pode se tornar rapidamente um problema.

Então, uma arquitetura mais adequada seria utilizar processamento assíncrono com fila de tarefas. Assim, teríamos, de forma simplificada:

Cliente (Texto) → Load Balancer (Distribuidor de Requisições) → API (FastAPI – stateless) → RabbitMQ (Fila de Tarefas) → Worker (Processador de Tarefas) → LLM (Ollama) → Banco de Dados (armazenamento do resultado)

------------------------------------------------------------------------

# Fim

Isso é tudo!