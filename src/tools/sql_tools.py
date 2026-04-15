from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
import os

def get_sql_tools():
    """Mengembalikan list tools untuk mengeksekusi query SQL di database SQLite."""
    db_path = "sqlite:///dataset/sql_jobs.db"
    db = SQLDatabase.from_uri(db_path)
    
    # Kita menggunakan LLM di sini untuk membantu toolkit mencerna skema database
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return toolkit.get_tools()