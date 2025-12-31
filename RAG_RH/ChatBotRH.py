import torch
import gc
import re
import os
import transformers
import uvicorn
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # Ajout de l'import manquant
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
HF_TOKEN = os.environ.get("HF_TOKEN")

# Création de l'application FastAPI
app = FastAPI()

# Configurer CORS pour permettre les requêtes de sources spécifiques
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chatbotrh.lot.fr"],  # Autoriser toutes les origines (à restreindre en production)
    allow_credentials=True,
    allow_methods=["POST"],  # Autoriser toutes les méthodes HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

# Libérer la mémoire GPU
gc.collect()
torch.cuda.empty_cache()

# Configurer le modèle
#model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
#model_id="Qwen/Qwen2.5-14B-Instruct"
model_id = 'mistralai/Mistral-7B-Instruct-v0.3'
model_config = AutoConfig.from_pretrained(model_id, token=HF_TOKEN)

# Charger le modèle avec quantization en 16 bits
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    config=model_config,
    device_map='cuda',
    torch_dtype=torch.float16,
    token=HF_TOKEN
)

tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    pad_token_id=128001,
    token=HF_TOKEN,
    padding_side="right",
    pad_token="</s>"
)

# S'assurer que le token pad est bien configuré
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id

# Créer un pipeline HuggingFace
query_pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="cuda",
    do_sample=True,
    top_k=5,
    top_p=0.95,
    temperature=0.1,
    max_new_tokens=512,  # Réduction du nombre de tokens générés
    trust_remote_code=True
)

llm = HuggingFacePipeline(pipeline=query_pipeline)

# Charger l'index FAISS
def load_faiss_index():
    model_path = 'OrdalieTech/Solon-embeddings-large-0.1'
    model_kwargs = {'device': 'cuda'}
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    #folder_path = "Vector_Storing_RH"
    folder_path ="Vector_Storage_RH_Final"
    index_name = "vectors_docs_RH"
    db = FAISS.load_local(folder_path, index_name=index_name, embeddings=embeddings, allow_dangerous_deserialization=True)
    return db

db = load_faiss_index()
retriever = db.as_retriever()

# Créer la chaîne de question-réponse
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    verbose=True,
)

# Fonction pour extraire uniquement la réponse utile
def extract_helpful_answer(text):
    pattern = r"Helpful Answer:\s*(.*?)(?=\n|$)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else "je suis désolé, je ne suis pas en mesure de répondre. Veuillez vous rapprocher de : (Numéro ou email)."

# Schéma de la requête
class QueryRequest(BaseModel):
    question: str

# Endpoint pour gérer les requêtes POST
@app.post("/predict")
def predict(query: QueryRequest):
    try:
        full_query = f"""[INST] Tu es un assistant IA expert en ressources humaines. Réponds à la question suivante en français, de manière concise et précise, en une seule phrase, en te basant uniquement sur les informations fournies dans le contexte. Si tu n'as pas suffisamment d'informations pour répondre, dis-le clairement.

Question : {query.question}

Contexte : {retriever}

[/INST]"""
        result = qa.invoke(full_query)
        result_text = extract_helpful_answer(result['result'].strip() if 'result' in result else result)

        return {"Réponse": result_text}
    except Exception as e:
        return {"Erreur": str(e)}

# Commande pour démarrer l'application avec Uvicorn
if __name__ == '__main__':
    gc.collect()
    torch.cuda.empty_cache()
    uvicorn.run("ChatBotRH:app", host="127.0.0.1", port=8000)
