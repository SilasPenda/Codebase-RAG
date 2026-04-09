# Codebase-RAG

### Codebase Retrieval-Augmented Generation Chatbot
An AI-powered assistant designed to help developers interact with a codebase by querying it in natural language. It extracts relevant code snippets, explains functionality, and provides insights based on repository content using embeddings, vector search, and LLM reasoning.

---

## Features

- **Repository Analysis: Processes your codebase to index functions, classes, and scripts.
- **Contextual Queries: Answers questions about code structure, logic, and dependencies.
- **Snippet Retrieval: Finds similar or relevant code segments to support explanations.
- **Interactive Chat: Provides clear, human-readable responses for any code-related query.
- **Extensible Collections: Supports multiple repositories or code collections.
- **Gradio UI: Easy-to-use interface for entering queries and viewing responses.
- **Dockerized: Ready for containerized deployment for easy sharing or hosting.

---

## Architecture

- **Embeddings & Vector Search:** Uses a vector database (e.g., Qdrant) to store and query policy rules and similar documents efficiently.
- **Large Language Model (LLM):** Applies an LLM to reason about compliance based on the context, retrieved policies, and related documents.
- **Gradio Frontend:** Provides an interactive web UI for document upload and compliance queries.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Access to OpenAI API or other LLM providers like Ollama
- Vector database setup (e.g., Qdrant, ChromaDB)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SilasPenda/Policy-Compliance-Agent
   cd policy-compliance-auditor

2. Create & activate virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate (Linux & Mac)
   ./.venv/Scripts/activate (Windows)
   
3. Install requirements:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Create .env file and add secrets

7. Launch API

   ```bash
   uvicorn deployment.api:app --reload

8. Start App

   ```bash
   python deployment/app.py
