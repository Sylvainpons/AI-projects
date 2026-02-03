import os
import threading  # Si tu en as besoin ailleurs, sinon retire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as api_router  # Import du router

app = FastAPI(title="Portable RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, on mettrait ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure le router (toutes les routes /api/* seront gérées par api_router)
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"status": "Active", "system": "Portable RAG v1.0"}