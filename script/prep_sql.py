import pandas as pd
import sqlite3
import os
import re

def extract_salary_features(salary_str):
    """
    Fungsi untuk mengekstrak angka dari string teks gaji.
    Mengembalikan tuple: (min_salary, max_salary, avg_salary)
    """
    # Jika data kosong atau Not Disclosed, kembalikan None (menjadi NULL di database)
    if pd.isna(salary_str) or salary_str == 'Not Disclosed' or salary_str == 'World Class Benefits':
        return None, None, None

    # Ubah ke string dan hapus titik & koma (pemisah ribuan) agar angka menyatu
    # Contoh: "Rp 7.500.000" menjadi "Rp 7500000"
    clean_str = str(salary_str).replace('.', '').replace(',', '')
    
    # Ekstrak semua kumpulan angka menggunakan Regex
    numbers = re.findall(r'\d+', clean_str)
    
    # Konversi ke float
    numbers = [float(n) for n in numbers]
    
    if len(numbers) == 0:
        return None, None, None
    elif len(numbers) == 1:
        # Jika hanya ada 1 angka (misal: "Rp 10.000.000 per month")
        return numbers[0], numbers[0], numbers[0]
    elif len(numbers) >= 2:
        # Jika ada range (misal: "Rp 7.500.000 - Rp 10.000.000")
        min_sal = min(numbers[0], numbers[1])
        max_sal = max(numbers[0], numbers[1])
        avg_sal = (min_sal + max_sal) / 2
        return min_sal, max_sal, avg_sal

def prepare_sql_database(csv_path: str, db_path: str, cleaned_csv_path: str):
    print(f"Membaca dataset dari {csv_path}...")
    df = pd.read_csv(csv_path)

    print("Membersihkan dan memformat data...")
    
    # 1. Menghapus kolom job_description 
    if 'job_description' in df.columns:
        df = df.drop(columns=['job_description'])

    # 2. Menangani nilai kosong (Missing Values) pada kolom dasar
    if 'salary' in df.columns:
        df['salary'] = df['salary'].fillna('Not Disclosed')
    
    if 'location' in df.columns:
        df['location'] = df['location'].fillna('Unknown')
    if 'work_type' in df.columns:
        df['work_type'] = df['work_type'].fillna('Unknown')

    # 3. Merapikan penulisan (Standardisasi)
    df['work_type'] = df['work_type'].str.strip().str.title()
    df['location'] = df['location'].str.strip().str.title()
    df['company_name'] = df['company_name'].str.strip()

    # 4. Feature Engineering: Ekstraksi Gaji Numerik (BARU)
    print("Mengekstrak data gaji numerik...")
    # Terapkan fungsi ekstraksi ke setiap baris di kolom 'salary'
    extracted_salaries = df['salary'].apply(extract_salary_features)
    
    # Buat 3 kolom baru dari hasil ekstraksi
    df['min_salary_numeric'] = [x[0] for x in extracted_salaries]
    df['max_salary_numeric'] = [x[1] for x in extracted_salaries]
    df['avg_salary_numeric'] = [x[2] for x in extracted_salaries]

    # Memastikan folder dataset ada
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Simpan ke CSV
    print(f"Menyimpan versi bersih ke CSV di {cleaned_csv_path}...")
    df.to_csv(cleaned_csv_path, index=False)

    print(f"Menyimpan ke database SQLite di {db_path}...")
    
    # Membuat koneksi SQLite
    conn = sqlite3.connect(db_path)
    
    # Memasukkan DataFrame ke dalam tabel SQL bernama 'jobs'
    df.to_sql('jobs', conn, if_exists='replace', index=False)
    
    # Cek skema tabel yang berhasil dibuat
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(jobs)")
    columns = cursor.fetchall()
    print("\nSkema Tabel 'jobs':")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
        
    conn.close()
    print("\nSelesai! Database sql_jobs.db siap digunakan oleh SQL Agent.")

if __name__ == "__main__":
    INPUT_CSV = 'dataset/jobs.csv'
    OUTPUT_DB = 'dataset/sql_jobs.db'
    CLEANED_CSV = 'dataset/cleaned_jobs.csv' 
    
    prepare_sql_database(INPUT_CSV, OUTPUT_DB, CLEANED_CSV)