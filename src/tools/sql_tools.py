import sqlite3
import os
from langchain.tools import tool

@tool("execute_sql_query")
def execute_sql_query(query: str) -> str:
    """Tool ini digunakan untuk menjalankan query SQL SELECT ke dalam database SQLite 'sql_jobs.db' untuk mendapatkan data lowongan pekerjaan. DILARANG eksekusi fitur manipulasi data/DROP."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "dataset", "sql_jobs.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return f"Data mentah: {str(rows)}"
    except Exception as e:
        return f"Terjadi kesalahan eksekusi query: {str(e)}"

def get_sql_tools():
    """Mengembalikan list berisi custom tool SQLite3 manual."""
    return [execute_sql_query]