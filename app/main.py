import uvicorn

if __name__ == "__main__":
    # executa a aplicação FastAPI
    uvicorn.run("api.incidente_endpoints:app", host="0.0.0.0", port=8000, reload=True)