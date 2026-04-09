import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import json
import numpy as np
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Must be set BEFORE importing Hugging Face modules
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_classic.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA

from src.utils import db_client_connect, get_llm, redis_client_connect, get_embedding_model
from deployment.schemas import Codebase, InsertCodebase
from deployment.templates import code_generation_template
from ingestion.code_ingestor import CodebaseIngestor

load_dotenv()

app = FastAPI(
    title="Codebase RAG API",
    description="API for retrieving relevant code snippets and generating code based on user queries.",
    version="1.0.0"
)

# Global objects to avoid re-initialization per request
redis = redis_client_connect()
collection_name = os.getenv("CODEBASE_COLLECTION_NAME")
embedding_model = None
llm_model = None
vector_store = None

# --- Health check ---
@app.get("/health")
async def health():
    return {"status": "ok"}

# --- Startup event: load models once ---
@app.on_event("startup")
async def startup_event():
    global embedding_model, llm_model, vector_store
    embedding_model = get_embedding_model()
    # embedding_model = HuggingFaceEmbeddings(model_name="microsoft/codebert-base")
    llm_model = get_llm()

    # # Initialize vector store once
    # vector_store = QdrantVectorStore.from_existing_collection(
    #     embedding=embedding_model,
    #     collection_name=collection_name,
    #     url=os.getenv("QDRANT_URL"),
    #     api_key=os.getenv("QDRANT_API_KEY")
    # )
    # print("Models and vector store loaded successfully!")
    print("LLM and embedding model loaded successfully!")

# --- Utility functions ---
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_similar_query_embedding(new_emb, session_id, threshold=0.88):
    keys = redis.lrange(session_id, 0, -1)
    for key_bytes in keys:
        key_data = json.loads(key_bytes)
        past_emb = key_data.get("embedding")
        if past_emb:
            similarity = cosine_similarity(np.array(new_emb), np.array(past_emb))
            if similarity >= threshold:
                return key_data["response"]
    return None


@app.post("/code/insert")
async def codebase_insert(info: InsertCodebase):
    # try:
    codebase_ingestor = CodebaseIngestor()
    collection_name = codebase_ingestor.run_pipeline(info.session_id, info.repo_path)
    return JSONResponse(content={"message": collection_name})
    
    # except Exception as e:
    #     return JSONResponse(content={"error": str(e)}, status_code=500)

# --- Main endpoint ---
@app.post("/code/check")
async def codebase_check(info: Codebase):
    # try:
    # Compute embedding
    query_embedding = embedding_model.embed_query(info.query)

    # Check Redis cache first
    # existing_response = find_similar_query_embedding(query_embedding, info.session_id)
    # if existing_response:
    #     return JSONResponse(content=existing_response)

    # Retriever
    # Initialize vector store once
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embedding_model,
        collection_name=info.collection_name,
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": info.top_k}
    )

    prompt = PromptTemplate(template=code_generation_template, input_variables=["question", "context"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain.invoke({"query": info.query})
    # print(result["source_documents"])

    # # Cache in Redis
    # entry = {"query": info.query, "embedding": query_embedding, "response": result}
    # redis.rpush(info.session_id, json.dumps(entry))
    # redis.expire(info.session_id, info.ttl)

    # return JSONResponse(content=result)
    return JSONResponse(content={"response": result["result"]})

    # except Exception as e:
    #     return JSONResponse(content={"error": str(e)}, status_code=500)