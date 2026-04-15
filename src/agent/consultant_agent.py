import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.messages import AIMessage
from src.agent.state import GraphState

def consultant_node(state: GraphState):
    print("[LOG] Consultant Agent aktif.")
    cv_text = state.get("cv_context", "")
    user_role = state.get("user_role", "jobseeker")
    
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    vector_store = QdrantVectorStore(
        client=client, 
        collection_name="indonesian_jobs", 
        embedding=OpenAIEmbeddings(model="text-embedding-3-small")
    )
    
    matched_jobs = vector_store.similarity_search(cv_text, k=3)
    job_context = "\n".join([j.page_content for j in matched_jobs])
    
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    if user_role == "hr":
        prompt = f"""
        Kamu adalah asisten HR. 
        PENTING: Jangan pernah berkata kamu tidak bisa membaca dokumen/file CV, karena teks dari dokumen tersebut SUDAH diekstrak ke dalam bentuk teks di bawah ini.
        
        Teks CV Kandidat:
        {cv_text}
        
        Lowongan Referensi:
        {job_context}
        
        Tugas: Apakah kandidat ini layak untuk direkrut berdasarkan teks di atas?
        """
    else:
        prompt = f"""
        Kamu adalah Konsultan Karir. 
        PENTING: Jangan pernah berkata kamu tidak bisa membaca dokumen/file CV, karena teks dari dokumen tersebut SUDAH diekstrak ke dalam bentuk teks di bawah ini.
        
        Teks CV User:
        {cv_text}
        
        Lowongan yang tersedia di database:
        {job_context}
        
        Tugas: Berikan rekomendasi lowongan yang cocok dan saran skill yang perlu ditingkatkan.
        """
        
    res = llm.invoke(prompt)
    return {"messages": [AIMessage(content=res.content)]}