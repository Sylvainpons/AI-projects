from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
from ..rag import ingest_file, query_rag, BASE_MOUNT_PATH  # Import relatif depuis app/

router = APIRouter(prefix="/api", tags=["api"])  # Prefix pour toutes les routes, et tags pour la doc Swagger

# Modèles (copiés de ton code, tu peux les déplacer dans un fichier models.py si tu veux)
class BrowseRequest(BaseModel):
    path: str = ""  # Chemin relatif (ex: "Documents/Projet")

class FileItem(BaseModel):
    name: str
    type: str  # "directory" ou "file"
    path: str  # Chemin complet relatif pour la navigation suivante

class IngestRequest(BaseModel):
    path: str  # Le dossier ou fichier à ingérer

class ChatRequest(BaseModel):
    question: str
    mode: str = "cloud"  # "local" ou "cloud"

@router.post("/browse", response_model=List[FileItem])
def browse_directory(request: BrowseRequest):
    """
    Explore un dossier spécifique du disque hôte.
    Sécurisé pour ne pas remonter plus haut que le point de montage.
    """
    clean_rel_path = request.path.strip("/")
    target_path = os.path.join(BASE_MOUNT_PATH, clean_rel_path)

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    if not os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="Ce n'est pas un dossier")

    items = []
    
    try:
        with os.scandir(target_path) as entries:
            for entry in entries:
                if entry.name.startswith('.'):
                    continue
                
                item_type = "directory" if entry.is_dir() else "file"
                next_path = os.path.join(clean_rel_path, entry.name)

                items.append(FileItem(
                    name=entry.name,
                    type=item_type,
                    path=next_path
                ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission refusée par Windows/Docker")

    items.sort(key=lambda x: (x.type != "directory", x.name.lower()))
    
    return items

@router.post("/ingest")
def ingest_data(request: IngestRequest):
    """
    Lance l'indexation d'un dossier ou fichier.
    """
    clean_rel_path = request.path.strip("/")
    target_path = os.path.join(BASE_MOUNT_PATH, clean_rel_path)

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Chemin introuvable")

    def process_path(path):
        results = []
        if os.path.isfile(path):
            res = ingest_file(path)
            results.append({path: res})
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.startswith('.'): continue
                    full_path = os.path.join(root, file)
                    try:
                        res = ingest_file(full_path)
                        results.append({file: res})
                    except Exception as e:
                        print(f"Erreur sur {file}: {e}")
        return results

    results = process_path(target_path)
    
    return {
        "message": "Ingestion terminée",
        "details": results
    }

@router.post("/chat")
def chat_with_docs(request: ChatRequest):
    """
    Pose une question aux documents ingérés.
    """
    result = query_rag(request.question, mode=request.mode)
    return result