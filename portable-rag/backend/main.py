import os
import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app.rag import ingest_file, query_rag, BASE_MOUNT_PATH

app = FastAPI(title="Portable RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, on mettrait ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Le point de montage dans le conteneur (fixe)

# Modèle de données pour la requête (ce que le Frontend envoie)
class BrowseRequest(BaseModel):
    path: str = ""  # Chemin relatif (ex: "Documents/Projet")

# Modèle de données pour un élément (Fichier ou Dossier)
class FileItem(BaseModel):
    name: str
    type: str  # "directory" ou "file"
    path: str  # Chemin complet relatif pour la navigation suivante
# Ajoute le champ 'mode' dans le modèle de requête
class ChatRequest(BaseModel):
    question: str
    mode: str = "local" # "local" ou "cloud"
@app.get("/")
def read_root():
    return {"status": "Active", "system": "Portable RAG v1.0"}

@app.post("/api/browse", response_model=List[FileItem])
def browse_directory(request: BrowseRequest):
    """
    Explore un dossier spécifique du disque hôte.
    Sécurisé pour ne pas remonter plus haut que le point de montage.
    """
    # Construction du chemin absolu interne au conteneur
    # On nettoie le chemin pour éviter les ".." (sécurité basique)
    clean_rel_path = request.path.strip("/")
    target_path = os.path.join(BASE_MOUNT_PATH, clean_rel_path)

    # Vérification que le dossier existe
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    if not os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="Ce n'est pas un dossier")

    items = []
    
    try:
        # On liste le contenu avec os.scandir (plus rapide que os.listdir)
        with os.scandir(target_path) as entries:
            for entry in entries:
                # On ignore les fichiers cachés (commençant par .) pour rester propre
                if entry.name.startswith('.'):
                    continue
                
                item_type = "directory" if entry.is_dir() else "file"
                
                # Le chemin qu'on renverra au front pour le prochain clic
                # Si on est à la racine, c'est juste le nom, sinon chemin/nom
                next_path = os.path.join(clean_rel_path, entry.name)

                items.append(FileItem(
                    name=entry.name,
                    type=item_type,
                    path=next_path
                ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission refusée par Windows/Docker")

    # On trie : Dossiers d'abord, puis fichiers (alphabétique)
    items.sort(key=lambda x: (x.type != "directory", x.name.lower()))
    
    return items

class IngestRequest(BaseModel):
    path: str # Le dossier ou fichier à ingérer

@app.post("/api/ingest")
def ingest_data(request: IngestRequest):
    """
    Lance l'indexation d'un dossier ou fichier.
    """
    clean_rel_path = request.path.strip("/")
    target_path = os.path.join(BASE_MOUNT_PATH, clean_rel_path)

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Chemin introuvable")

    # Fonction interne pour traiter récursivement
    def process_path(path):
        results = []
        if os.path.isfile(path):
             # C'est un fichier unique
             res = ingest_file(path)
             results.append({path: res})
        elif os.path.isdir(path):
            # C'est un dossier, on parcourt tout
            for root, _, files in os.walk(path):
                for file in files:
                    if file.startswith('.'): continue # Ignore fichiers cachés
                    full_path = os.path.join(root, file)
                    try:
                        res = ingest_file(full_path)
                        results.append({file: res})
                    except Exception as e:
                        print(f"Erreur sur {file}: {e}")
        return results

    # NOTE : Pour un vrai projet pro, on utiliserait "Celery" ou "BackgroundTasks"
    # Ici on fait simple pour la démo immédiate.
    results = process_path(target_path)
    
    return {
        "message": "Ingestion terminée",
        "details": results
    }

class ChatRequest(BaseModel):
    question: str
    mode:str = "cloud"

@app.post("/api/chat")
def chat_with_docs(request: ChatRequest):
    """
    Pose une question aux documents ingérés.
    """
    result = query_rag(request.question, mode=request.mode)

    return result
