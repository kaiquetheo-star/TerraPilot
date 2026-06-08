from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TerraPilot API", version="0.1.0")

class HealthResponse(BaseModel):
    status: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "online", "version": "0.1.0"}

@app.get("/")
async def root():
    return {"message": "TerraPilot API is running"}