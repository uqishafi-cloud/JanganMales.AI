import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.messages import AIMessage
from src.agent.state import GraphState

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent
from src.tools.consultant_tools import match_jobs_by_cv

def consultant_node(state: GraphState):
    print("[LOG] Consultant Agent aktif.")
    cv_text = state.get("cv_context", "")
    user_role = state.get("user_role", "jobseeker")
    
    llm = ChatOpenAI(model=os.getenv("LLM_MODEL"))
        
    langfuse_client = Langfuse()
    prompt_template = langfuse_client.get_prompt("consultant_agent_prompt", label="latest")
    
    if user_role == "hr":
        role_title = "asisten HR"
        task_instruction = "Langkah 3: Berdasarkan lowongan yang didapat dari tool, apakah kandidat ini layak untuk direkrut? Berikan alasannya."
        kandidat_tag = "Kandidat"
    else:
        role_title = "Konsultan Karir"
        task_instruction = "Langkah 3: Berikan rekomendasi lowongan yang cocok dari tool pencarian dan saran skill yang perlu ditingkatkan."
        kandidat_tag = "User"
        
    system_prompt = prompt_template.compile(
        role_title=role_title,
        kandidat_tag=kandidat_tag,
        cv_text=cv_text,
        task_instruction=task_instruction
    )
    
    # Buat agent yang akan memakai tool pencocokan CV
    consultant_agent = create_react_agent(llm, tools=[match_jobs_by_cv], prompt=system_prompt)
    
    langfuse_handler = CallbackHandler()
    res = consultant_agent.invoke(
        {"messages": state.get("messages", [])}, 
        config={"callbacks": [langfuse_handler]}
    )
    
    return {"messages": [res["messages"][-1]]}