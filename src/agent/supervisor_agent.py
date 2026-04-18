from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from src.agent.state import GraphState
from src.agent.sql_agent import sql_agent_node
from src.agent.rag_agent import rag_agent_node
from src.agent.consultant_agent import consultant_node

def supervisor_node(state: GraphState):
    print("[LOG] Supervisor Agent aktif.")
    user_msg = state["messages"][-1].content
    
    # Prioritas ke Consultant jika ada CV
    if state.get("cv_context"):
        print("[LOG] CV terdeteksi, mengarahkan ke Consultant Agent.")
        return {"next_route": "consultant_agent"}
        
    from langfuse import Langfuse
    from langfuse.langchain import CallbackHandler
    import os
    
    langfuse_client = Langfuse()
    prompt_template = langfuse_client.get_prompt("supervisor_agent_prompt", label="latest")
    
    system_prompt = prompt_template.compile(user_msg=user_msg)
    
    llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)
    langfuse_handler = CallbackHandler()
    
    intent_res = llm.invoke(system_prompt, config={"callbacks": [langfuse_handler]})
    intent = intent_res.content.strip().lower()
    
    print(f"[LOG] Intent asli LLM: '{intent}'")
    
    # Logika penentuan
    if "sql" in intent:
        route = "sql_agent"
    elif "rag" in intent:
        route = "rag_agent"
    elif "consult" in intent:
        route = "consultant_agent"
    else:
        # Fallback jika LLM bertele-tele
        if any(keyword in user_msg.lower() for keyword in ["berapa", "jumlah", "gaji", "statistik", "lokasi"]):
            route = "sql_agent"
        elif any(keyword in user_msg.lower() for keyword in ["evaluasi", "cv", "resume", "rekomendasi"]):
            route = "consultant_agent"
        else:
            route = "rag_agent"
        
    print(f"[LOG] Rute terpilih: {route}")
    return {"next_route": route}

workflow = StateGraph(GraphState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("sql_agent", sql_agent_node)
workflow.add_node("rag_agent", rag_agent_node)
workflow.add_node("consultant_agent", consultant_node)

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor", 
    lambda x: x["next_route"],
    {"sql_agent": "sql_agent", 
     "rag_agent": "rag_agent", 
     "consultant_agent": "consultant_agent"
     }
)
workflow.add_edge("sql_agent", END)
workflow.add_edge("rag_agent", END)
workflow.add_edge("consultant_agent", END)

janganmales_agent = workflow.compile()