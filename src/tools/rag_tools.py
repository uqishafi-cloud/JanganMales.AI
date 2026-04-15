from langchain.tools import tool
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os
from dotenv import load_dotenv

load_dotenv()

# Inisialisasi Qdrant
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=os.getenv("QDRANT_COLLECTION_NAME", "job_postings"),
    embedding=embeddings,
)

class JobSearchInput(BaseModel):
    query: str = Field(description="Kata kunci pencarian kualifikasi, skill, atau deskripsi pekerjaan.")
    job_title: str = Field(default=None, description="Filter nama posisi jika ada (misal: 'Data Analyst')")
    company_name: str = Field(default=None, description="Filter nama perusahaan jika ada (misal: 'PT ABC')")

@tool("search_job_postings", args_schema=JobSearchInput)
def search_job_postings(query: str, job_title: str = None, company_name: str = None) -> str:
    """Gunakan tool ini HANYA jika user mencari informasi dari dalam deskripsi pekerjaan, kualifikasi, atau skill."""
    
    must_conditions = []
    if job_title:
        must_conditions.append(models.FieldCondition(
            key="metadata.job_title", match=models.MatchValue(value=job_title)))
    if company_name:
        must_conditions.append(models.FieldCondition(
            key="metadata.company_name", match=models.MatchValue(value=company_name)))
            
    filter_kondisi = models.Filter(must=must_conditions) if must_conditions else None
    hasil = vector_store.similarity_search(query=query, k=4, filter=filter_kondisi)
    
    if not hasil:
        return "Tidak ditemukan lowongan yang cocok."
        
    return "\n\n".join([f"Posisi: {d.metadata.get('job_title')}\nPerusahaan: {d.metadata.get('company_name')}\nDetail: {d.page_content}" for d in hasil])