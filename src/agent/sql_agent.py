import sqlite3
import os
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from src.agent.state import GraphState
from src.tools.sql_tools import get_sql_tools
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

def sql_agent_node(state: GraphState):
    print("[LOG] SQL Agent aktif.")
    user_role = state.get("user_role", "jobseeker")
    
    # Ambil prompt dari Langfuse agar disembunyikan dari kode
    langfuse_client = Langfuse()
    prompt_template = langfuse_client.get_prompt("sql_agent_prompt", label="latest")
    
    # Compile prompt dan pasang variabel dinamis (misal: user_role)
    system_prompt = prompt_template.compile(user_role=user_role)
    
    llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)
    sql_tools = get_sql_tools()
    
    # Buat agent mandiri yang menggunakan system prompt dari Langfuse dan toolkit SQL
    sql_agent = create_react_agent(llm, tools=sql_tools, prompt=system_prompt)
    
    # Callback handler untuk langfuse
    langfuse_handler = CallbackHandler()
    
    # Jalankan agent dengan seluruh riwayat obrolan user dan pass callbacks
    response = sql_agent.invoke(
        {"messages": state["messages"]},
        config={"callbacks": [langfuse_handler]}
    )
    
    return {"messages": [response["messages"][-1]]}