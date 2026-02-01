// On définit l'URL directe du backend
const API_BASE_URL = "http://localhost:8000";

export interface FileItem {
  name: string;
  type: "directory" | "file";
  path: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: { source: string; path: string }[];
}

// 1. Explorer les dossiers
export const browseFiles = async (path: string = ""): Promise<FileItem[]> => {
  // On utilise l'URL complète maintenant
  const res = await fetch(`${API_BASE_URL}/api/browse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  if (!res.ok) throw new Error("Erreur lors du chargement des fichiers");
  return res.json();
};

// 2. Ingérer
export const ingestPath = async (path: string) => {
  const res = await fetch(`${API_BASE_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  if (!res.ok) throw new Error("Erreur lors de l'ingestion");
  return res.json();
};

// 3. Discuter
export const chatWithRag = async (question: string) => {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("Erreur du Chatbot");
  return res.json();
};