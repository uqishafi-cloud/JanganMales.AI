import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from src.agent.state import GraphState
from src.tools.rag_tools import search_job_postings
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

def rag_agent_node(state: GraphState):
    print("[LOG] RAG Agent aktif.")
    
    # Ambil prompt dari Langfuse agar disembunyikan dari kode
    langfuse_client = Langfuse()
    prompt_template = langfuse_client.get_prompt("rag_agent_prompt", label="latest")
    system_prompt = prompt_template.compile()
    
    llm = ChatOpenAI(model=os.getenv("LLM_MODEL"))
    
    # Buat agent mandiri yang menggunakan system prompt dari Langfuse
    rag_agent = create_react_agent(llm, tools=[search_job_postings], prompt=system_prompt)
    
    # Callback handler untuk langfuse
    langfuse_handler = CallbackHandler()
    
    # Jalankan agent dengan seluruh riwayat obrolan user dan pass callbacks
    response = rag_agent.invoke(
        {"messages": state["messages"]},
        config={"callbacks": [langfuse_handler]}
    )
    
    return {"messages": [response["messages"][-1]]}