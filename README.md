# JanganMales.AI — *Kerja, kerja, kerja... menuju 19 juta lapangan pekerjaan* 🚀

**Multi-Agent AI Career Assistant & Job Matching System**

JanganMales.AI adalah platform cerdas berbasis AI yang dirancang untuk membantu pencari kerja mengoptimalkan profil mereka dan menemukan lowongan pekerjaan yang paling relevan. Menggunakan arsitektur **Multi-Agent** yang ditenagai oleh **LangGraph**, sistem ini mampu berinteraksi, menganalisis, dan memberikan rekomendasi karier secara personal.

---

## ✨ Fitur Utama
*   **Intelligent CV Extraction**: Mengekstrak teks dari CV format PDF, DOCX, hingga Gambar (menggunakan GPT-4o Vision) dengan akurasi tinggi.
*   **Multi-Agent Orchestration**: Alur percakapan yang cerdas menggunakan Supervisor Agent untuk mengarahkan pengguna ke agen spesialis yang tepat.
*   **Semantic Job Matching (RAG)**: Mencocokkan kualifikasi pengguna dengan database lowongan menggunakan teknologi *Vector Search*.
*   **Data Driven Insights (SQL)**: Memberikan statistik gaji, lokasi, dan tren pekerjaan berdasarkan query database yang presisi.
*   **Career Consulting**: Memberikan saran perbaikan CV dan strategi karier berdasarkan profil pengguna.

---
## 👥 User Roles & Fitur Khusus

Platform **JanganMales.AI** dirancang dengan sistem cerdas yang mampu membedakan kebutuhan pengguna berdasarkan perannya. Berikut adalah pembagian role dan fitur yang tersedia:

### **1. Role: Jobseeker (Tanpa Login)**
Role ini ditujukan bagi para pencari kerja yang ingin mendapatkan bantuan instan tanpa perlu melakukan proses registrasi atau login.

* **Identifikasi Otomatis:** Chatbot akan mengenali secara otomatis bahwa pengguna adalah seorang *jobseeker*.
* **Fitur Utama:**
    * **Pencarian Pekerjaan:** Bertanya langsung kepada AI mengenai lowongan yang relevan berdasarkan skill atau posisi.
    * **Konsultasi CV:** Diskusi interaktif mengenai cara memperbaiki struktur CV agar lebih profesional dan menarik bagi rekruter.
    * **Bimbingan Karir:** Konsultasi umum mengenai persiapan interview, negosiasi gaji, dan tips dunia kerja.


### **2. Role: HR / Recruiter (Login Diperlukan)**
Role ini memberikan akses ke alat manajemen talenta yang lebih canggih. Untuk masuk sebagai HR, Anda dapat menggunakan akun dummy berikut:

* **Akun Dummy HR:**
    * **Username:** `herman`
    * **Password:** `hermannakal`
* **Identifikasi Otomatis:** Setelah login, chatbot akan mengubah konteks komunikasinya menjadi asisten rekrutmen/HR.
* **Fitur Unggulan: CV Evaluator**
    Fitur ini dirancang khusus untuk mempercepat proses *screening* kandidat dalam jumlah banyak.
    * **Panel Kiri (Input Kriteria):** HR dapat memasukkan kriteria spesifik pekerjaan, keahlian wajib, dan preferensi kualifikasi yang dicari.
    * **Panel Kanan (Upload Massal):** Fitur untuk mengunggah banyak file CV sekaligus (format PDF/DOCX).
    * **Analisis AI:** AI akan melakukan analisa mendalam untuk mencocokkan kriteria di panel kiri dengan data CV di panel kanan, memberikan skor relevansi, dan membantu HR memutuskan kandidat terbaik secara objektif.

---

## 🏗️ Arsitektur Sistem (Modular Multi-Agent)
Proyek ini menggunakan paradigma **Multi-Agent Workflow** di mana setiap modul memiliki tanggung jawab spesifik:

1.  **Supervisor Agent**: "Otak" utama yang menganalisis intensi pengguna dan menentukan kapan harus memanggil agen spesialis.
2.  **Consultant Agent**: Bertanggung jawab untuk mengevaluasi CV dan memberikan rekomendasi pekerjaan berdasarkan profil kandidat.
3.  **SQL Agent**: Menangani pertanyaan terstruktur seperti statistik gaji, jumlah lowongan per lokasi, dan tren data.
4.  **RAG Agent**: Menangani pencarian informasi tidak terstruktur dalam basis pengetahuan menggunakan database vektor.

---

## 📂 Struktur Project
```text
JanganMales.ai/
├── src/
│   ├── agent/                   # Logika AI Agents (LangGraph Workflow)
│   │   ├── supervisor_agent.py  # Router & Intent Classifier
│   │   ├── consultant_agent.py  # Spesialis Evaluasi CV & Karier
│   │   ├── rag_agent.py         # Spesialis Pencarian Semantik (Knowledge Base)
│   │   ├── sql_agent.py         # Spesialis Query Database Terstruktur
│   │   └── state.py             # Definisi State & Schema Percakapan
│   ├── api/                     # Backend Service (FastAPI)
│   │   └── main.py              # REST API untuk Chat, Upload CV, & Integrasi Agent
│   ├── frontend/                # User Interface (Streamlit)
│   │   └── app.py               # Web Dashboard Interaktif
│   └── tools/                   # Custom Tools (Function Calling)
│       ├── consultant_tools.py  # Tool pencocokan profil via Vector Store
│       ├── rag_tools.py         # Tool pencarian dokumen pintar
│       └── sql_tools.py         # Tool eksekusi aman SQL Query
├── dataset/                     # Sumber data lowongan (Raw Excel/CSV)
├── Dockerfile                   # Konfigurasi Containerisasi Produksi
├── docker-compose.yml           # Konfigurasi Orkestrasi Lokal
├── pyproject.toml               # Manajemen Dependensi & Project (Poetry)
└── README.md                    # Dokumentasi Utama
```

---

## 🚀 Panduan Menjalankan Project

### A. Persiapan Prasyarat
- **Python 3.11+**
- **Poetry**: Digunakan untuk mengelola library dan virtual environment. [Instalasi Poetry](https://python-poetry.org/docs/#installation).
- **Docker Desktop**: Diperlukan jika ingin menjalankan menggunakan kontainer.

---

### B. Setup Lokal (Manual)
Gunakan metode ini jika Anda ingin melakukan pengembangan (development) dan debugging secara langsung.

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/username/JanganMales.AI.git
    cd JanganMales.AI
    ```

2.  **Install Dependensi**:
    Gunakan Poetry untuk mengunci versi library yang digunakan.
    ```bash
    poetry install
    ```

3.  **Konfigurasi Environment**:
    Buat file bernama `.env` di direktori root dan masukkan API Keys Anda:
    ```bash
    QDRANT_URL=
    QDRANT_API_KEY=
    OPENAI_API_KEY=
    QDRANT_COLLECTION_NAME=
    LLM_MODEL=
    EMBEDDING_MODEL=
    LANGFUSE_SECRET_KEY=
    LANGFUSE_PUBLIC_KEY=
    LANGFUSE_BASE_URL=
    GCLOUD_API_URL=
    # ... sesuaikan dengan kebutuhan tools
    ```

4.  **Jalankan API Backend**:
    Gunakan Uvicorn untuk menjalankan server FastAPI.
    ```bash
    # Masuk ke virtualenv poetry
    poetry shell
    # Jalankan server
    python -m uvicorn src.api.main:app --reload --port 8000
    ```

5.  **Jalankan UI Frontend (Tab Terminal Baru)**:
    ```bash
    # Masuk ke virtualenv poetry
    poetry shell
    # Jalankan Streamlit
    streamlit run src/frontend/app.py
    ```
    Buka `http://localhost:8501` di browser Anda.

---

### C. Setup Menggunakan Docker (Direkomendasikan)
Metode ini adalah yang termudah karena secara otomatis mengonfigurasi jaringan antara backend dan frontend.

1.  Pastikan Docker sudah berjalan di komputer Anda.
2.  Jalankan perintah berikut:
    ```bash
    docker compose up --build
    ```
3.  Sistem akan otomatis:
    - Melakukan build image dari `Dockerfile`.
    - Menjalankan **Backend** di `http://localhost:8000`.
    - Menjalankan **Frontend** di `http://localhost:8080`.

---

## ☁️ Deployment (Google Cloud Run)

Langkah-langkah profesional untuk memindahkan aplikasi ke production Google Cloud:

### 1. Build Image Produksi
Kirimkan source code ke Google Cloud Build untuk dibuatkan image Docker yang dioptimalkan.
```bash
gcloud builds submit --tag gcr.io/<PROJECT_ID>/janganmales-ai
```

### 2. Deploy Layanan API (Backend)
```bash
gcloud run deploy janganmales-backend \
  --image gcr.io/<PROJECT_ID>/janganmales-ai \
  --region=us-central1 \
  --allow-unauthenticated
```
*Catatan: Simpan URL Backend yang Anda dapatkan.*

### 3. Deploy Layanan Website (Frontend)
Kita mendeploy image yang sama, namun memerintahkan kontainer untuk menjalankan perintah Streamlit.
```bash
gcloud run deploy janganmales-frontend \
  --image gcr.io/<PROJECT_ID>/janganmales-ai \
  --set-env-vars="API_URL=<URL_BACKEND_ANDA>" \
  --command="streamlit","run","src/frontend/app.py","--server.port","8080","--server.address","0.0.0.0" \
  --region=us-central1 \
  --allow-unauthenticated
```

---

## 🛠️ Tech Stack
*   **AI Framework**: LangChain, LangGraph, OpenAI (GPT-4o-mini).
*   **Backend**: FastAPI, Uvicorn (Asynchronous Python).
*   **Frontend**: Streamlit.
*   **Database**: Qdrant (Vector DB), SQLite/Pandas (Structured Storage).
*   **Infrastructure**: Docker, Google Cloud Run, GCR.

---