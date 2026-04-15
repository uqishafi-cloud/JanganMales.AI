import pandas as pd
import os
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Setup dasar
load_dotenv()
logging.basicConfig(level=logging.INFO)

class JobExtraction(BaseModel):
    skills: list[str] = Field(description="Daftar keahlian teknis dan soft skill")
    experience: str = Field(description="Syarat pengalaman kerja")
    education: str = Field(description="Syarat pendidikan minimal")
    responsibilities: str = Field(description="Ringkasan tugas utama")

def main():
    excel_path = 'dataset/jobs.csv'
    output_json = 'dataset/processed_jobs.json'
    limit = 473

    # Inisialisasi LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0, 
        api_key=os.getenv("OPENAI_API_KEY")
    )
    structured_llm = llm.with_structured_output(JobExtraction)

    logging.info(f"Membaca data dari {excel_path} (limit: {limit})...")
    
    if excel_path.endswith('.csv'):
        df = pd.read_csv(excel_path)
    else:
        df = pd.read_excel(excel_path)
        
    df = df.head(limit)
    extracted_data = []
    
    for idx, row in df.iterrows():
        job_title = str(row.get('job_title', 'Unknown'))
        company = str(row.get('company_name', 'Unknown'))
        job_desc = str(row.get('job_description', ''))
        
        if not job_desc.strip():
            continue

        logging.info(f"Mengekstrak baris {idx} | Posisi: {job_title}...")
        
        try:
            extracted = structured_llm.invoke(
                f"Ekstrak informasi berikut dari deskripsi pekerjaan ini:\n\n{job_desc}"
            )
            dense_chunk = (
                f"Posisi: {job_title}\nPerusahaan: {company}\n"
                f"Skill Dibutuhkan: {', '.join(extracted.skills)}\n"
                f"Pengalaman: {extracted.experience}\n"
                f"Pendidikan: {extracted.education}\n"
                f"Tugas Utama: {extracted.responsibilities}"
            )
        except Exception as e:
            logging.error(f"Gagal mengekstrak baris {idx}: {e}")
            dense_chunk = f"Posisi: {job_title}\nPerusahaan: {company}\nDeskripsi: {job_desc}"

        extracted_data.append({
            "page_content": dense_chunk,
            "metadata": {
                'job_title': job_title,
                'company_name': company,
                'location': str(row.get('location', 'Unknown')),
                'work_type': str(row.get('work_type', 'Unknown')),
                'row_index': idx,
                'source': excel_path,
                'original_description': job_desc
            }
        })
        
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        
    logging.info(f"SELESAI! {len(extracted_data)} dokumen berhasil disimpan ke {output_json}")

if __name__ == "__main__":
    main()