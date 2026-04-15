import pandas as pd
import sqlite3
import os

def prepare_sql_database(csv_path: str, db_path: str, cleaned_csv_path: str):
    print(f"Membaca dataset dari {csv_path}...")
    df = pd.read_csv(csv_path)

    print("Membersihkan dan memformat data...")
    
    # 1. Menghapus kolom job_description 
    # (Karena RAG Agent sudah mengurus teks panjang, SQL Agent fokus pada data terstruktur)
    if 'job_description' in df.columns:
        df = df.drop(columns=['job_description'])

    # 2. Menangani nilai kosong (Missing Values)
    # Jika tidak ada gaji, tulis 'Not Disclosed' agar AI tidak bingung saat user tanya gaji
    if 'salary' in df.columns:
        df['salary'] = df['salary'].fillna('Not Disclosed')
    
    # Pastikan kolom lokasi dan work_type tidak kosong
    if 'location' in df.columns:
        df['location'] = df['location'].fillna('Unknown')
    if 'work_type' in df.columns:
        df['work_type'] = df['work_type'].fillna('Unknown')

    # 3. Merapikan penulisan (Standardisasi)
    # Menghilangkan spasi berlebih dan merapikan huruf kapital agar mudah difilter oleh SQL
    df['work_type'] = df['work_type'].str.strip().str.title()
    df['location'] = df['location'].str.strip().str.title()
    df['company_name'] = df['company_name'].str.strip()

    # Memastikan folder dataset ada
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Simpan ke CSV
    print(f"Menyimpan versi bersih ke CSV di {cleaned_csv_path}...")
    df.to_csv(cleaned_csv_path, index=False)

    print(f"Menyimpan ke database SQLite di {db_path}...")
    
    # Membuat koneksi SQLite
    conn = sqlite3.connect(db_path)
    
    # Memasukkan DataFrame ke dalam tabel SQL bernama 'jobs'
    # if_exists='replace' artinya jika file db sudah ada, akan ditimpa dengan data baru yang bersih
    df.to_sql('jobs', conn, if_exists='replace', index=False)
    
    # Cek skema tabel yang berhasil dibuat
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(jobs)")
    columns = cursor.fetchall()
    print("\nSkema Tabel 'jobs':")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
        
    conn.close()
    print("\nSelesai! Database jobs.db siap digunakan oleh SQL Agent.")

if __name__ == "__main__":
    # Sesuaikan path ini dengan lokasi file CSV Anda
    INPUT_CSV = 'dataset/jobs.csv'
    OUTPUT_DB = 'dataset/sql_jobs.db'
    CLEANED_CSV = 'dataset/cleaned_jobs.csv' # <-- File CSV output
    
    prepare_sql_database(INPUT_CSV, OUTPUT_DB, CLEANED_CSV)