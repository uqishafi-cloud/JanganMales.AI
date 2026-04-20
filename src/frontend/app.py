import streamlit as st
import requests
import json

API_URL = st.secrets["API_URL"]

st.set_page_config(page_title="JanganMales.AI", layout="wide")

if "role" not in st.session_state: st.session_state.role = "jobseeker"
if "cv_text" not in st.session_state: st.session_state.cv_text = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "last_processed_file" not in st.session_state: st.session_state.last_processed_file = ""
# Sidebar: Sistem Login & Navigasi

st.sidebar.title("Portal Akses")
if st.session_state.role == "jobseeker":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Login Khusus HR")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), "hr_users.json")
            with open(db_path, "r") as f:
                hr_db = json.load(f)
            if username in hr_db and hr_db[username].get("password") == password:
                if hr_db[username].get("role") == "hr":
                    st.session_state.role = "hr"
                    st.session_state.user_name = hr_db[username].get("name", username)
                    st.session_state.chat_history = []
                    st.session_state.cv_text = ""
                    st.rerun()
                else:
                    st.sidebar.error("Akun ini tidak memiliki akses HR.")
            else:
                st.sidebar.error("Username atau Password tidak valid.")
        except FileNotFoundError:
            st.sidebar.error("Database sistem HR tidak ditemukan.")
else:
    st.sidebar.success("Sesi Aktif")
    st.sidebar.info(f"Login sebagai:\n{st.session_state.user_name}")
    
    st.sidebar.markdown("---")
    hr_menu = st.sidebar.radio("Menu HR:", ["Chatbot AI", "CV Evaluator"])
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout"):
        st.session_state.role = "jobseeker"
        st.session_state.user_name = ""
        st.session_state.chat_history = []
        st.session_state.cv_text = ""
        st.rerun()

def process_uploaded_cv(file_obj):
    files = {"file": (file_obj.name, file_obj.getvalue())}
    res = requests.post(f"{API_URL}/upload-cv", files=files)
    if res.status_code == 200:
        return res.json()["cv_text"]
    return None

# PAGE 1: MODE JOBSEEKER ATAU HR CHATBOT
if st.session_state.role == "jobseeker" or (st.session_state.role == "hr" and hr_menu == "Chatbot AI"):
    st.title("JanganMales.AI - Kerja Dong!" if st.session_state.role == "jobseeker" else "JanganMales.AI - "
    "Yuk Biar Pada Dapat Kerjaan")
    st.subheader("Terbuka 19 juta lapangan pekerjaan!" if st.session_state.role == "jobseeker" else f"Halo {st.session_state.user_name}")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            # --- TAMBAHAN KODE EXPANDER ---
            # Jika yang membalas adalah AI (assistant) dan ada data agen-nya, munculkan Expander
            if msg["role"] == "assistant" and "agent_used" in msg:
                with st.expander("🛠️ Lihat Proses AI (Log Agent)"):
                    st.write(f"🔍 **Diarahkan ke:** `{msg['agent_used']}`")
                    st.success(f"Tugas berhasil dieksekusi oleh {msg['agent_used']}!")
            # ------------------------------
            
            # Tampilkan jawaban utama
            st.write(msg["content"])

    st.markdown("---")
    
    with st.expander("📎 Lampirkan CV/Resume (Opsional)", expanded=False):
        uploaded_file = st.file_uploader(
            "Pilih file dokumen Anda", 
            max_upload_size=10, 
            type=["pdf", "docx", "jpg", "jpeg", "png"],
            label_visibility="collapsed" # Menyembunyikan judul bawaan agar lebih bersih
        )
        if uploaded_file and uploaded_file.size > 10 * 1024 * 1024:
            st.error("Ukuran file melebihi batas maksimal 10 MB.")
            uploaded_file = None # Membatalkan file jika kebesaran
    if st.session_state.cv_text:
        st.success("Terdapat CV yang sedang aktif di dalam memori AI.")

    user_input = st.chat_input("Ketik pesan atau pertanyaan di sini...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"): 
            st.write(user_input)
        
        with st.spinner(f"Sistem sedang menganalisis..."):
            if uploaded_file and uploaded_file.name != st.session_state.last_processed_file:
                st.toast("Mengekstrak file dokumen...")
                extracted_text = process_uploaded_cv(uploaded_file)
                if extracted_text:
                    st.session_state.cv_text = extracted_text
                    st.session_state.last_processed_file = uploaded_file.name
                else:
                    st.error("Gagal membaca dokumen, chat dilanjutkan tanpa dokumen.")
            
            payload = {
                "message": user_input,
                "history": st.session_state.chat_history[:-1],  #tambahan ini
                "cv_text": st.session_state.cv_text,
                "role": st.session_state.role
            }
            res = requests.post(f"{API_URL}/chat", json=payload)
            
            if res.status_code == 200:
                data = res.json()
                
                # Mengambil jawaban (mendukung key 'reply' atau 'response' dari API)
                answer = data.get("reply", data.get("response", "Maaf, ada kesalahan."))
                
                if "debug_log" in data:
                    st.toast(f"🔥 [AGENT LOG]: {data['debug_log']}")
                
                # Mengambil nama agen dari Backend (Default jika tidak ada data: "AI Agent")
                agent_used = data.get("agent_used", "AI Agent")
                
                # Menyimpan jawaban DAN nama agen ke dalam history agar bisa dilacak
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer,
                    "agent_used": agent_used
                })
                st.rerun()
            else:
                st.error("Gagal terhubung ke server utama.")

# PAGE 2: MODE HR EVALUATOR CV
elif st.session_state.role == "hr" and hr_menu == "CV Evaluator":
    st.title("CV Evaluator")
    st.markdown("Fitur ini memungkinkan Anda menilai banyak kandidat sekaligus berdasarkan kriteria spesifik.")

    with st.form("evaluator_form", border=True):
        col_left, col_right = st.columns(2)
        
        with col_right:
            st.subheader("Area Unggah Dokumen")
            st.caption("Anda dapat mengunggah beberapa file CV sekaligus.")
            batch_files = st.file_uploader(
                "Unggah CV Kandidat",
                max_upload_size=10, 
                type=["pdf", "docx", "jpg", "png"], 
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="hr_file_uploader"
            )

        with col_left:
            st.subheader("Kriteria Pekerjaan")
            st.caption("Tentukan syarat wajib yang harus dimiliki kandidat.")
            criteria_input = st.text_area(
                "Kriteria Input", 
                placeholder="Contoh: \n- Minimal S1 Sastra Mesin" \
                "\n- Menguasai 15 bahasa" \
                "\n- Mampu menerbangkan pesawat tempur" \
                "\n- Pengalaman menjadi presiden selama 32 tahun", 
                height=150,
                label_visibility="collapsed",
                key="hr_criteria_input"
            )

        st.markdown("---")

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            submit_eval = st.form_submit_button("Analyze", type="primary", use_container_width=True)
        with btn_col2:
            reset_eval = st.form_submit_button("Reset Form", type="secondary", use_container_width=True)

    if reset_eval:
        if "hr_file_uploader" in st.session_state:
            del st.session_state["hr_file_uploader"]
        if "hr_criteria_input" in st.session_state:
            del st.session_state["hr_criteria_input"]
        
        st.rerun()

    if submit_eval:
        if not criteria_input:
            st.warning("Harap isi kriteria pekerjaan terlebih dahulu.")
        elif not batch_files:
            st.warning("Harap unggah minimal 1 CV kandidat.")
        else:
            st.subheader("Hasil Analisis")
            
            for file in batch_files:
                with st.spinner(f"Menganalisis {file.name}..."):
                    cv_text = process_uploaded_cv(file)
                    
                    if cv_text:
                        payload = {"criteria": criteria_input, "cv_text": cv_text}
                        res = requests.post(f"{API_URL}/evaluate-cvs", json=payload)
                        
                        if res.status_code == 200:
                            full_eval = res.json()["evaluation"]
                            
                            if "SANGAT COCOK" in full_eval.upper():
                                label_header = f"[✅ SANGAT COCOK] - {file.name}"
                            elif "TIDAK COCOK" in full_eval.upper():
                                label_header = f"[❌ TIDAK COCOK] - {file.name}"
                            elif "KURANG COCOK" in full_eval.upper():
                                label_header = f"[⚠️ KURANG COCOK] - {file.name}"
                            else:
                                label_header = f"[HASIL EVALUASI] - {file.name}"

                            with st.expander(label_header):
                                st.write(full_eval)
                        else:
                            st.error(f"Gagal mengevaluasi {file.name}. Status: {res.status_code} | Detail: {res.text}")
                    else:
                        st.error(f"Gagal mengekstrak teks dari {file.name}. Status: {res.status_code} | Detail: {res.text}")

