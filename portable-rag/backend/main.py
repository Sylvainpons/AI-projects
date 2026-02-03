import os
import threading  # Si tu en as besoin ailleurs, sinon retire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.rag import ingest_file, query_rag, BASE_MOUNT_PATH
from .routers.api import router as api_router
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