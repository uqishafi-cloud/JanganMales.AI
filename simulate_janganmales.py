import os
from dotenv import load_dotenv
load_dotenv()

from src.agent.supervisor_agent import janganmales_agent
from langchain_core.messages import HumanMessage

def run_test(query, cv_text=None, role="jobseeker"):
    print(f"\n--- TESTING QUERY: '{query}' ---")
    inputs = {
        "messages": [HumanMessage(content=query)],
        "user_role": role,
        "cv_context": cv_text
    }
    
    # Eksekusi graph
    try:
        config = {"configurable": {"thread_id": "test_thread"}}
        output = janganmales_agent.invoke(inputs, config=config)
        
        print(f"ROUTE TERPILIH: {output.get('next_route')}")
        print(f"HASIL AKHIR:\n{output['messages'][-1].content}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print("-" * 40)

if __name__ == "__main__":
    # Test 1: SQL Agent (Statistik/Data Terstruktur)
    run_test("Berapa banyak jumlah lowongan pekerjaan yang ada di database sekarang?")
    
    # Test 2: RAG Agent (Deskriptif/Pencarian Kualifikasi)
    run_test("Apa saja kualifikasi umum untuk posisi Backend Engineer?")
    
    # Test 3: Consultant Agent (Evaluasi CV)
    cv_dummy = """
    Nama: Budi Santoso
    Skill: Python, SQL, FastAPI, Docker.
    Pengalaman: 2 tahun sebagai Junior Backend Developer.
    """
    run_test("Tolong beri rekomendasi kerja berdasarkan CV saya ini.", cv_text=cv_dummy)
