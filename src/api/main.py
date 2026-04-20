import os
from dotenv import load_dotenv
load_dotenv()
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import PyPDF2, docx, io, uvicorn
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.agent.supervisor_agent import janganmales_agent

app = FastAPI(title="JanganMales.AI API")

#tambahan ini
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = [] #tambahan ini   
    cv_text: str = ""
    role: str = "jobseeker"
class EvaluationRequest(BaseModel):
    criteria: str
    cv_text: str
    
@app.post("/upload-cv")
async def process_cv(file: UploadFile = File(...)):
    filename = file.filename.lower()
    allowed_ext = (".pdf", ".docx", ".jpg", ".jpeg", ".png")
    
    if not filename.endswith(allowed_ext):
        raise HTTPException(status_code=400, detail="Format tidak didukung. Gunakan PDF, DOCX, atau JPG/PNG.")
    
    try:
        content = await file.read()
        raw_text = ""
        
        # File Teks (PDF/DOCX)
        if filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            raw_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            raw_text = "\n".join([p.text for p in doc.paragraphs])
            
        # File Gambar
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            print("[INFO] Menggunakan GPT-4o-mini Vision untuk membaca gambar...")
            base64_image = base64.b64encode(content).decode("utf-8")
            llm_vision = ChatOpenAI(model="gpt-4o-mini", max_tokens=1500)
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Baca seluruh teks dalam gambar CV ini dengan sangat teliti. Pertahankan format aslinya (Pendidikan, Pengalaman, Skill)."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            )
            response = llm_vision.invoke([message])
            raw_text = response.content

        if not raw_text.strip():
            raise ValueError("Tidak ada teks yang dapat diekstrak.")
            
        return {"cv_text": raw_text.strip()}
        
    except Exception as e:
        print(f"[ERROR] Ekstraksi CV gagal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    print(f"[DEBUG API] Pesan masuk: '{req.message}'")
    print(f"[DEBUG API] Panjang teks CV yang diterima: {len(req.cv_text)} karakter")
    
    # Konversi history dari frontend ke format LangChain
    messages = []
    for m in req.history:
        if m.role == "user":
            messages.append(HumanMessage(content=m.content))
        else:
            messages.append(AIMessage(content=m.content))
    
    # Tambahkan pesan terbaru
    messages.append(HumanMessage(content=req.message))

    inputs = {
        "messages": messages,
        "cv_context": req.cv_text,
        "user_role": req.role
    }
    try:
        result = janganmales_agent.invoke(inputs)
        return {"reply": result["messages"][-1].content}
    except Exception as e:
        print(f"[ERROR] Agent gagal: {e}")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan pada sistem agen.")
    
@app.post("/evaluate-cvs")
async def evaluate_cvs(req: EvaluationRequest):
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        eval_prompt = f"""
        Kamu adalah Asisten HR Senior yang bertugas menyortir CV kandidat secara objektif.
        
        KRITERIA PEKERJAAN YANG DICARI:
        {req.criteria}
        
        TEKS CV KANDIDAT:
        {req.cv_text}
        
        Tugasmu:
        1. Berikan KESIMPULAN SINGKAT di awal: "SANGAT COCOK", "KURANG COCOK", atau "TIDAK COCOK".
        2. Buat daftar (bullet points) poin-poin kriteria apa saja yang TERPENUHI oleh kandidat.
        3. Buat daftar (bullet points) poin-poin kriteria apa saja yang TIDAK TERPENUHI (jika ada).
        4. Berikan sedikit saran apakah kandidat ini layak dipanggil wawancara.
        """
        
        response = llm.invoke(eval_prompt)
        return {"evaluation": response.content}
        
    except Exception as e:
        print(f"[ERROR API] Gagal evaluasi batch: {e}")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan saat evaluasi.")
        
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port)