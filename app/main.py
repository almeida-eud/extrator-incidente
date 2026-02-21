import uvicorn
from fastapi import FastAPI

if __name__ == "__main__":
    # executa a aplicação FastAPI definida em app.api:app
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)