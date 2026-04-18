from langchain.tools import tool
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
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

embeddings_model = os.getenv("EMBEDDING_MODEL")
if not embeddings_model:
    embeddings_model = "text-embedding-3-small"
embeddings = OpenAIEmbeddings(model=embeddings_model)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=os.getenv("QDRANT_COLLECTION_NAME", "indonesian_jobs"),
    embedding=embeddings,
)

class CVMatchInput(BaseModel):
    skills_summary: str = Field(description="Ringkasan skill, pengalaman, dan kualifikasi yang telah Anda ekstrak dari CV kandidat.")

@tool("match_jobs_by_cv", args_schema=CVMatchInput)
def match_jobs_by_cv(skills_summary: str) -> str:
    """Gunakan tool ini SESUDAH mendapatkan instruksi dari prompt untuk mencocokkan profil kandidat dengan database lowongan perusahaan. Masukkan sekumpulan skill dari CV."""
    
    hasil = vector_store.similarity_search(query=skills_summary, k=3)
    
    if not hasil:
        return "Tidak ditemukan lowongan yang cocok di database."
        
    return "\n\n".join([f"Posisi: {d.metadata.get('job_title')}\nPerusahaan: {d.metadata.get('company_name')}\nDetail: {d.page_content}" for d in hasil])
