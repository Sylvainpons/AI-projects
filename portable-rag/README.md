# 🚀 Portable RAG Agent (포터블 RAG 에이전트)

> **A Dockerized, Plug & Play Retrieval Augmented Generation System.** > **도커 기반의 플러그 앤 플레이 RAG 시스템 (Local & Hybrid Inference).**

![Python](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Infrastructure-Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![VectorDB](https://img.shields.io/badge/VectorDB-Qdrant-b9305c?style=flat-square)
![AI](https://img.shields.io/badge/AI-LangChain_&_Ollama-white?style=flat-square)

---

## 🇬🇧 English Description

### Project Overview
This project is a **High-Performance Portable RAG Solution** designed to be infrastructure-agnostic. It leverages **Docker** for orchestration and **FastAPI** for the backend logic.

The key innovation lies in its **"Dynamic Host Mounting"** capability: the containerized agent can securely access, analyze, and vectorize files from the host machine (Windows/Mac/Linux) instantly, without requiring manual data migration.

### Key Features
* **🏗 Clean Architecture:** Separation of concerns between Ingestion, Vectorization, and Retrieval.
* **🔌 Plug & Play:** One command (`docker-compose up`) to start the entire stack.
* **🧠 Intelligent Routing:** Automatically detects file types (PDF, Python Code, YAML, Markdown) and applies specific chunking strategies (e.g., `RecursiveCharacterTextSplitter` for code).
* **⚡ CPU Optimized:** Uses `FastEmbed` (ONNX) and Quantized LLMs (Ollama) to run efficiently on standard consumer hardware.
* **📂 Dynamic File System:** Real-time exploration of the host file system via a secure API.

### Tech Stack
* **Backend:** Python 3.11, FastAPI, Pydantic.
* **Orchestration:** Docker, LangChain.
* **Database:** Qdrant (Rust-based Vector DB).
* **Inference:** Ollama (Local LLM) / Open Architectures.

---

## 🇰🇷 프로젝트 소개 (Korean Description)

### 개요 (Overview)
이 프로젝트는 인프라에 구애받지 않는 **고성능 포터블 RAG 솔루션**입니다. **Docker**를 활용한 오케스트레이션과 **FastAPI** 기반의 백엔드 로직을 결합했습니다.

가장 큰 특징은 **"동적 호스트 마운팅(Dynamic Host Mounting)"** 기술입니다. 컨테이너화된 에이전트가 호스트 머신(Windows/Mac/Linux)의 파일에 안전하게 접근하여, 수동으로 데이터를 이동할 필요 없이 즉시 분석 및 벡터화를 수행합니다.

### 주요 기능 (Key Features)
* **🏗 클린 아키텍처:** 데이터 수집(Ingestion), 벡터화(Vectorization), 검색(Retrieval) 로직의 명확한 분리.
* **🔌 플러그 앤 플레이:** `docker-compose up` 명령어 하나로 전체 서비스 스택 실행.
* **🧠 지능형 라우팅:** 파일 유형(PDF, Python Code, YAML, Markdown)을 자동으로 감지하고, 이에 맞는 최적의 청킹(Chunking) 전략을 적용합니다.
* **⚡ CPU 최적화:** `FastEmbed` (ONNX)와 양자화된 LLM(Ollama)을 사용하여 일반 CPU 환경에서도 고성능을 보장합니다.
* **📂 동적 파일 시스템:** 보안 API를 통해 호스트 파일 시스템을 실시간으로 탐색할 수 있습니다.

### 기술 스택 (Tech Stack)
* **Backend:** Python 3.11, FastAPI, Pydantic.
* **Orchestration:** Docker, LangChain.
* **Database:** Qdrant (Rust 기반 벡터 데이터베이스).
* **Inference:** Ollama (로컬 LLM) / Open Architectures.

---

## 🛠 Getting Started (시작하기)

### 1. Prerequisites
* Docker & Docker Compose installed.
* Ollama installed locally (for LLM inference).

### 2. Configuration
Create a `.env` file in the root directory:
```bash
# Windows Example
HOST_PATH=C:/Users/YourName

# Mac/Linux Example
HOST_PATH=/Users/yourname