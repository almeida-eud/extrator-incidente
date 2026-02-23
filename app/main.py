import uvicorn

# executa a aplicação FastAPI

if __name__ == "__main__":
    uvicorn.run("api.incidente_endpoints:app", host="0.0.0.0", port=8000, reload=True)