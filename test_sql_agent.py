from dotenv import load_dotenv
load_dotenv()

from src.agent.sql_agent import sql_agent_node
from langchain_core.messages import HumanMessage

try:
    state = {
        "messages": [HumanMessage(content="Tolong berikan 3 daftar lowongan pekerjaan Data Analyst.")],
        "user_role": "jobseeker"
    }
    
    output = sql_agent_node(state)
    print("\n\n====== HASIL LLM ======\n")
    print(output["messages"][-1].content)
    
except Exception as e:
    print("\n\n====== TERJADI ERROR ======\n")
    import traceback
    traceback.print_exc()
