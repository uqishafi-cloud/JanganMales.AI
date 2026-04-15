import os
import json
import logging
from uuid import uuid4
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

# Setup dasar
load_dotenv()
logging.basicConfig(level=logging.INFO)

def main():
    json_path = 'dataset/processed_jobs.json'
    batch_size = 50

    if not os.path.exists(json_path):
        logging.error(f"File {json_path} tidak ditemukan! Jalankan chunking_database.py terlebih dahulu.")
        return

    # 1. Load data dari JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
        
    documents = [
        Document(page_content=item["page_content"], metadata=item["metadata"]) 
        for item in data_list
    ]
    logging.info(f"Berhasil memuat {len(documents)} dokumen dari {json_path}.")

    # 2. Inisialisasi Qdrant dan Embeddings
    logging.info("Inisialisasi Qdrant client (dengan timeout 60 detik)...")
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=60.0  # Timeout diperbesar untuk menghindari WriteTimeout
    )
            
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    collection_name = os.getenv("QDRANT_COLLECTION_NAME")
    collections = qdrant_client.get_collections().collections
    
    if collection_name not in [col.name for col in collections]:
        logging.info(f"Membuat koleksi baru: {collection_name}...")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
    
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embeddings,
    )

    # 3. Upload dengan sistem Batch
    logging.info("Memulai proses upload ke Qdrant...")
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i : i + batch_size]
        batch_uuids = [str(uuid4()) for _ in range(len(batch_docs))]
        
        logging.info(f"Mengunggah dokumen ke {i+1} hingga {i+len(batch_docs)} (Total: {len(documents)})...")
        vector_store.add_documents(documents=batch_docs, ids=batch_uuids)
        
    logging.info("SELESAI! Semua dokumen berhasil diunggah ke Qdrant.")

if __name__ == "__main__":
    main()