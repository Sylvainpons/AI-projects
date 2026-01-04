from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

# =========================
# Configuration
# =========================

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "korea_ai_docs"

# ⚠️ IMPORTANT
# Cette dimension doit correspondre à TON modèle d'embeddings
# Exemple :
# - all-MiniLM-L6-v2 -> 384
# - bge-large -> 1024
# - e5-large -> 1024
VECTOR_SIZE = 2560

# =========================
# Connexion Qdrant
# =========================

client = QdrantClient(url=QDRANT_URL)

# =========================
# Vérifier si la collection existe
# =========================

existing_collections = [
    collection.name for collection in client.get_collections().collections
]

if COLLECTION_NAME in existing_collections:
    print(f" Collection '{COLLECTION_NAME}' existe déjà.")
else:
    print(f" Création de la collection '{COLLECTION_NAME}'...")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )

    print(" Collection créée avec succès.")
