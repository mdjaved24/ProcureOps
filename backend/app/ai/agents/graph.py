from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.ai.agents.state import ProcureOpsState
from app.ai.agents.nodes.guardrail_node import guardrail_node
from app.ai.agents.nodes.operation_resolution_node import operation_resolution_node
from app.ai.agents.nodes.context_resolution_node import context_resolution_node
from app.ai.agents.nodes.hitl_node import hitl_node
from app.ai.agents.nodes.action_execution_node import action_execution_node
from app.ai.agents.nodes.rag_node import rag_node
from app.ai.agents.nodes.live_data_node import live_data_node
from app.ai.agents.nodes.general_node import general_node
from app.ai.agents.nodes.memory_node import memory_retrieval_node, memory_update_node
from app.ai.agents.nodes.response_node import response_node
from app.ai.agents.nodes.router_node import router_node


class ProcureOpsGraph:
    """Simplified ProcureOps Agent Graph with LLM-based operation resolution."""
    
    @staticmethod
    def build_graph():
        workflow = StateGraph(ProcureOpsState)
        
        # ============================================================
        # ADD NODES
        # ============================================================
        workflow.add_node("guardrail", guardrail_node)
        workflow.add_node("memory_retrieval", memory_retrieval_node)
        workflow.add_node("operation_resolution", operation_resolution_node)
        workflow.add_node("context_resolution", context_resolution_node)
        workflow.add_node("hitl", hitl_node)
        workflow.add_node("action_execution", action_execution_node)
        workflow.add_node("router", router_node)
        workflow.add_node("rag", rag_node)
        workflow.add_node("live_data", live_data_node)
        workflow.add_node("general", general_node)
        workflow.add_node("memory_update", memory_update_node)
        workflow.add_node("response", response_node)
        
        # ============================================================
        # ADD EDGES - SEQUENTIAL ONLY
        # ============================================================
        
        # 1. Guardrail → Memory → Operation → Context
        workflow.add_edge(START, "guardrail")
        workflow.add_conditional_edges(
            "guardrail",
            lambda state: "continue" if state.get("guardrail_allowed", True) else "block",
            {
                "continue": "memory_retrieval",
                "block": END,
            }
        )
        
        workflow.add_edge("memory_retrieval", "operation_resolution")
        workflow.add_edge("operation_resolution", "context_resolution")
        workflow.add_edge("context_resolution", "hitl")
        
        # 2. HITL → Action or Router
        workflow.add_conditional_edges(
            "hitl",
            lambda state: (
                "action_execution"
                if state.get("hitl_required") and state.get("hitl_status") in ["APPROVE", "REJECT"]
                else "router"
            ),
            {
                "action_execution": "action_execution",
                "router": "router",
            }
        )
        
        # 3. Action execution goes directly to response
        workflow.add_edge("action_execution", "memory_update")
        workflow.add_edge("memory_update", "response")
        
        # 4. Router → Processing Nodes based on data_access_type
        workflow.add_conditional_edges(
            "router",
            lambda state: state.get("data_access_type", "GENERAL"),
            {
                "LIVE_DATA": "live_data",
                "KNOWLEDGE": "rag",
                "GENERAL": "general",
            }
        )
        
        # 5. All processing nodes → Memory Update → Response
        workflow.add_edge("live_data", "memory_update")
        workflow.add_edge("rag", "memory_update")
        workflow.add_edge("general", "memory_update")
        workflow.add_edge("memory_update", "response")
        workflow.add_edge("response", END)
        
        # ============================================================
        # COMPILE
        # ============================================================
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)