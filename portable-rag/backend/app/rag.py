import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_core.retrievers import BaseRetriever
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
BASE_MOUNT_PATH = "/mnt/host_files"
# Configuration Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "my_knowledge_base"

def get_vector_store():
    """Initialise la connexion à Qdrant avec des embeddings légers (CPU friendly)"""
    
    # 1. Choix du modèle d'embedding
    # FastEmbed est très rapide et tourne sur CPU sans GPU.
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    # 2. Connexion au client
    client = QdrantClient(url=QDRANT_URL)

    if not client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"Création de la collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384, # Taille spécifique au modèle BAAI/bge-small
                distance=models.Distance.COSINE
            )
        )
    
    # 3. Création de l'objet VectorStore
    # On vérifie si la collection existe, sinon on la laisse se créer auto
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

def ingest_file(file_path: str):
    """
    Fonction intelligente qui détecte le type de fichier, 
    le charge, le découpe et l'indexe.
    """
    
    # --- 1. ROUTING (Choix du Loader) ---
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".py"):
        # Pour le code, on veut garder la structure
        loader = TextLoader(file_path)
    elif file_path.endswith((".txt", ".md", ".json",".yml", ".yaml", ".dockerfile", "Dockerfile")):
        loader = TextLoader(file_path, autodetect_encoding=True)
    else:
        # On ignore les types inconnus (images, zip, etc.) pour l'instant
        return {"status": "ignored", "reason": "unsupported format"}

    documents = loader.load()

    # --- 2. SPLITTING (Découpage Intelligent) ---
    # Si c'est du code Python, on utilise un séparateur spécifique
    if file_path.endswith(".py"):
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=500, chunk_overlap=50
        )
    else:
        # Pour le texte normal
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        
    chunks = splitter.split_documents(documents)

    # Ajout de métadonnées (important pour filtrer plus tard)
    for chunk in chunks:
        chunk.metadata["source"] = file_path
        chunk.metadata["filename"] = os.path.basename(file_path)

    # --- 3. INDEXING (Vectorisation) ---
    vector_store = get_vector_store()
    
    # Ajout des documents dans Qdrant
    vector_store.add_documents(chunks)
    
    return {"status": "success", "chunks_created": len(chunks)}

def query_rag(query_text: str):
    """
    RAG Complet : Recherche + Génération par LLM
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    # 1. Récupération des documents pertinents
    docs = retriever.invoke(query_text)
    
    # Préparation du contexte sous forme de texte pour le LLM
    context_text = "\n\n".join([doc.page_content for doc in docs])
    
    # 2. Configuration du LLM (Ollama sur l'hôte)
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    
    # On utilise un modèle léger et performant (mistral, llama3, ou phi)
    llm = ChatOllama(
        model="mistral", # Assure-toi d'avoir fait 'ollama pull mistral'
        base_url=ollama_url,
        temperature=0
    )

    # 3. Le Prompt (Les instructions au Cerveau)
    template = """Tu es un assistant expert technique. 
    Utilise le contexte suivant pour répondre à la question de l'utilisateur.
    Si la réponse n'est pas dans le contexte, dis simplement que tu ne sais pas.
    Réponds en français de manière professionnelle.

    Contexte:
    {context}

    Question:
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 4. Création de la chaîne (Chain) et exécution
    chain = prompt | llm | StrOutputParser()
    
    try:
        response_text = chain.invoke({"context": context_text, "question": query_text})
    except Exception as e:
        response_text = f"Erreur de connexion au LLM (Ollama est-il lancé ?): {str(e)}"

    # 5. On renvoie la réponse + les sources (pour la transparence)
    results = []
    for doc in docs:
        results.append({
            "source": doc.metadata.get("filename", "inconnu"),
            "path": doc.metadata.get("source", "inconnu")
        })
        
    return {
        "answer": response_text,
        "sources": results
    }