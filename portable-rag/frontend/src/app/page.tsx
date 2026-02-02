"use client";

import { useState, useEffect, useRef } from "react";
import { browseFiles, ingestPath, chatWithRag, FileItem, ChatMessage } from "@/src/utils/api";
import { Folder, FileCode, FileText, HardDrive, Send, Loader2, Bot, User, ChevronLeft,Zap, Cpu } from "lucide-react";
import clsx from "clsx";
import MarkdownRenderer from "@/src/components/MarkdownRenderer";

export default function Home() {
  // --- STATE : Explorateur de Fichiers ---
  const [isCloudMode, setIsCloudMode] = useState(false);
  const [currentPath, setCurrentPath] = useState(""); // Où sommes-nous ?
  const [files, setFiles] = useState<FileItem[]>([]); // Liste des fichiers
  const [selectedPath, setSelectedPath] = useState<string | null>(null); // Fichier sélectionné
  const [isIngesting, setIsIngesting] = useState(false); // Chargement ingestion

  // --- STATE : Chat ---
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "Bonjour ! Sélectionnez un dossier à analyser pour commencer." }
  ]);
  const [input, setInput] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // 1. Charger les fichiers au démarrage et à chaque changement de dossier
  useEffect(() => {
    loadFiles(currentPath);
  }, [currentPath]);

  // Scroll automatique vers le bas du chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadFiles = async (path: string) => {
    try {
      const data = await browseFiles(path);
      setFiles(data);
    } catch (error) {
      console.error(error);
      alert("Impossible de lire le dossier (Docker a-t-il les droits ?)");
    }
  };

  // Navigation : Entrer dans un dossier
  const handleNavigate = (folderName: string) => {
    // Si currentPath est vide, c'est "folderName", sinon "currentPath/folderName"
    const newPath = currentPath ? `${currentPath}/${folderName}` : folderName;
    setCurrentPath(newPath);
    setSelectedPath(null); // On désélectionne quand on change de vue
  };

  // Navigation : Remonter d'un cran (..)
  const handleGoUp = () => {
    if (!currentPath) return;
    const parts = currentPath.split("/");
    parts.pop(); // Enlève le dernier dossier
    setCurrentPath(parts.join("/"));
  };

  // Action : Lancer l'ingestion
  const handleIngest = async () => {
    if (!selectedPath) return;
    setIsIngesting(true);
    try {
      // Message temporaire
      setMessages(prev => [...prev, { role: "assistant", content: `🚀 Analyse de ${selectedPath} en cours...` }]);
      
      const res = await ingestPath(selectedPath);
      
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: `✅ Analyse terminée ! J'ai mémorisé ${res.chunks_created || res.details?.length || "plusieurs"} fragments. Posez-moi une question.` 
      }]);
    } catch (e) {
      alert("Erreur d'ingestion");
    } finally {
      setIsIngesting(false);
    }
  };

  // Action : Envoyer un message
  const handleSendChat = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setInput("");
    
    // Ajout message utilisateur
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setIsChatting(true);

    try {
      const res = await chatWithRag(userMsg, isCloudMode ? "cloud" : "local");
      // Ajout réponse bot
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: res.answer,
        sources: res.sources 
      }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: "❌ Erreur de connexion au cerveau." }]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <main className="flex h-screen w-full bg-zinc-950 text-zinc-100 font-sans overflow-hidden">
      
      {/* --- GAUCHE : Explorateur de Fichiers --- */}
      <section className="w-1/3 border-r border-zinc-800 flex flex-col bg-zinc-900/50">
        {/* Header Explorateur */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <h2 className="font-semibold text-sm tracking-wider text-zinc-400 flex items-center gap-2">
            <HardDrive className="w-4 h-4" /> EXPLORATEUR
          </h2>
          {currentPath && (
            <button onClick={handleGoUp} className="p-1 hover:bg-zinc-800 rounded text-zinc-400">
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Fil d'ariane (Breadcrumb) */}
        <div className="px-4 py-2 text-xs text-zinc-500 font-mono border-b border-zinc-800/50 truncate">
          ROOT/{currentPath}
        </div>

        {/* Liste des fichiers */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {files.map((file) => (
            <div
              key={file.name}
              onClick={() => setSelectedPath(file.path)}
              onDoubleClick={() => file.type === 'directory' && handleNavigate(file.name)}
              className={clsx(
                "flex items-center gap-3 p-2 rounded cursor-pointer transition-colors text-sm",
                selectedPath === file.path ? "bg-blue-600/20 text-blue-200 border border-blue-500/30" : "hover:bg-zinc-800 text-zinc-300"
              )}
            >
              {file.type === "directory" ? (
                <Folder className="w-4 h-4 text-yellow-500 fill-yellow-500/20" />
              ) : file.name.endsWith('.py') ? (
                <FileCode className="w-4 h-4 text-green-400" />
              ) : (
                <FileText className="w-4 h-4 text-zinc-500" />
              )}
              <span className="truncate">{file.name}</span>
            </div>
          ))}
        </div>

        {/* Footer Explorateur : Bouton Ingest */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-900">
          <button
            disabled={!selectedPath || isIngesting}
            onClick={handleIngest}
            className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded flex items-center justify-center gap-2 transition-all"
          >
            {isIngesting ? <Loader2 className="w-4 h-4 animate-spin" /> : "⚡ Analyser la sélection"}
          </button>
          <p className="text-[10px] text-zinc-600 mt-2 text-center">
            Sélectionnez un dossier ou un fichier pour l'ajouter au contexte.
          </p>
        </div>
      </section>

      {/* --- DROITE : Chat Interface --- */}
      <section className="flex-1 flex flex-col bg-zinc-950">
        {/* Header Chat */}
        <div className="h-14 border-b border-zinc-800 flex items-center justify-between px-6 bg-zinc-900/30">
          
          {/* Titre */}
          <div className="flex items-center gap-3">
             <div className={clsx("w-2 h-2 rounded-full shadow-[0_0_8px]", isCloudMode ? "bg-orange-500 shadow-orange-500/50" : "bg-green-500 shadow-green-500/50")}></div>
             <div>
               <h1 className="font-semibold text-zinc-200 text-sm">Portable RAG</h1>
               <p className="text-[10px] text-zinc-500 font-mono">
                 {isCloudMode ? "Moteur: Llama3-70b (Groq Cloud)" : "Moteur: Mistral (Local CPU)"}
               </p>
             </div>
          </div>

          {/* Le Bouton Switch */}
          <button 
            onClick={() => setIsCloudMode(!isCloudMode)}
            className={clsx(
              "flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all text-xs font-medium",
              isCloudMode 
                ? "bg-orange-900/20 border-orange-500/30 text-orange-200 hover:bg-orange-900/40" 
                : "bg-zinc-800 border-zinc-700 text-zinc-300 hover:bg-zinc-700"
            )}
          >
            {isCloudMode ? (
              <>
                <span>Mode Turbo</span>
                <Zap className="w-3 h-3 fill-orange-400 text-orange-400" />
              </>
            ) : (
              <>
                <span>Mode Privé</span>
                <Cpu className="w-3 h-3" />
              </>
            )}
          </button>
        </div>

        {/* Zone des messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={clsx("flex gap-4", msg.role === "user" ? "justify-end" : "justify-start")}>
              
              {/* Icône Robot (si Assistant) */}
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded bg-indigo-500/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                  <Bot className="w-5 h-5 text-indigo-400" />
                </div>
              )}

              {/* Bulle de message */}
              <div className={clsx(
                "max-w-[85%] p-4 rounded-lg text-sm leading-relaxed overflow-hidden",
                msg.role === "user" ? "bg-zinc-800 text-zinc-100" : "bg-zinc-900/50 text-zinc-300 border border-zinc-800"
              )}>
                
                {/* Contenu du message : Markdown pour le Bot, Texte simple pour l'User */}
                {msg.role === "assistant" ? (
                  <MarkdownRenderer content={msg.content} />
                ) : (
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                )}
                
                {/* Affichage des sources (si disponibles) */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-zinc-800/50">
                    <p className="text-xs font-semibold text-zinc-500 mb-2">Sources utilisées :</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((src, i) => (
                        <span key={i} className="text-[10px] px-2 py-1 bg-zinc-950 border border-zinc-800 rounded text-zinc-400 font-mono truncate max-w-[200px]">
                          {src.source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Icône User (si User) */}
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded bg-zinc-800 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-zinc-400" />
                </div>
              )}
            </div>
          ))}
          
          {isChatting && (
             <div className="flex gap-4">
                <div className="w-8 h-8 rounded bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                  <Bot className="w-5 h-5 text-indigo-400" />
                </div>
                <div className="flex items-center gap-2 text-zinc-500 text-sm">
                   <Loader2 className="w-4 h-4 animate-spin" /> Réflexion en cours...
                </div>
             </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Zone */}
        <div className="p-4 bg-zinc-900 border-t border-zinc-800">
          <div className="max-w-4xl mx-auto relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
              placeholder="Posez une question sur vos documents..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-4 pr-12 py-3 text-sm text-zinc-200 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all placeholder:text-zinc-600"
            />
            <button 
              onClick={handleSendChat}
              disabled={!input.trim() || isChatting}
              className="absolute right-2 p-1.5 bg-indigo-600 hover:bg-indigo-500 rounded text-white disabled:opacity-50 disabled:bg-zinc-800 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-center text-[10px] text-zinc-600 mt-2">
            Portable RAG v1.0 • Powered by Ollama & Qdrant
          </p>
        </div>
      </section>
    </main>
  );
}