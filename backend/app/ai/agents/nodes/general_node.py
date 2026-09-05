import json
from langchain_core.messages import HumanMessage, SystemMessage
from app.ai.agents.state import ProcureOpsState
from app.ai.llm.groq_llm import get_llm


def general_node(state: ProcureOpsState) -> dict:
    """
    Handle general queries that don't fit into RAG or LIVE_DATA.
    This is the fallback for unknown operations.
    """
    user_query = state.get("user_query", "")
    retrieved_memories = state.get("retrieved_memories", [])
    
    memory_context = json.dumps(
        retrieved_memories,
        indent=2,
        default=str,
    )
    
    system_prompt = """
    You are ProcureOps AI, a helpful assistant for a procurement management application.
    
    Answer the user's question in a helpful, professional manner.
    
    If the question is about procurement concepts but you don't have specific data:
    - Provide general guidance
    - Suggest what the user can do in the application
    - Offer to help with specific queries
    
    If the question is unrelated to procurement:
    - Politely let the user know you're a procurement assistant
    - Suggest asking about procurement-related topics
    
    Keep answers clear and concise.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"""
        User Question:
        {user_query}
        
        Relevant Long-Term User Memory:
        {memory_context}
        """
        ),
    ]
    
    llm = get_llm()
    response = llm.invoke(messages)
    
    return {
        "response": response.content.strip(),
        "sources": [],
    }