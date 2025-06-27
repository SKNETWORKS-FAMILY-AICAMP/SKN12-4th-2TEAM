# app/services/rag_pipeline.py

from pathlib import Path
import os
from app.services.rag_chatbot import (
    expand_query,
    extract_metadata_filters,
    get_relevant_context,
    generate_response,
)
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FEW_SHOT_PATH = DATA_DIR / "few_shot_examples.json"
CHROMA_DIR = DATA_DIR / "chromadb"

# Chroma Collection 초기화
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from chromadb.utils import embedding_functions
from pathlib import Path
import chromadb

# 현재 파일 기준: app/services/rag_chatbot.py → app/data/
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chromadb"

# ChromaDB 클라이언트 초기화
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    
 # 임베딩 함수 설정 -> ChromaDB에서 사용하는 임베딩 함수
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="jhgan/ko-sroberta-multitask"
    )
collection = chroma_client.get_collection(
        name="ppt_documents_collection",
        embedding_function=embedding_function
    )

def run_rag_pipeline(user_query: str) -> dict:
    expanded = expand_query(user_query)
    filters = extract_metadata_filters(user_query)
    context, metadata = get_relevant_context(expanded, collection, metadata_filters=filters)
    answer, relevance = generate_response(user_query, context, metadata)
    # print(answer)
    return {
        "answer": answer,
        "relevance": relevance
    }
