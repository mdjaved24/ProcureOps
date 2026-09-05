from langgraph.types import Command

from app.ai.agents.graph import ProcureOpsGraph


class ProcureOpsAgentService:
    """Service for interacting with the ProcureOps agent graph."""
    
    _graph = None

    @classmethod
    def get_graph(cls):
        """Get or create the agent graph instance."""
        if cls._graph is None:
            cls._graph = ProcureOpsGraph.build_graph()
        return cls._graph

    @classmethod
    async def process_query(
        cls,
        user_query: str,
        conversation_id: str,
        user_id: int,
    ) -> dict:
        """
        Process a user query through the agent graph.
        """
        graph = cls.get_graph()

        config = {
            "configurable": {
                "thread_id": conversation_id,
            }
        }

        result = await graph.ainvoke(
            {
                "user_query": user_query,
                "user_id": user_id,
            },
            config=config,
        )

        # Ensure status is present
        if "status" not in result:
            if result.get("error"):
                result["status"] = "error"
            elif result.get("response"):
                result["status"] = "completed"
            elif result.get("hitl_request"):
                result["status"] = "pending_approval"
            else:
                result["status"] = "completed"

        return result

    @classmethod
    async def resume_query(
        cls,
        conversation_id: str,
        decision: str,
        user_id: int,
    ) -> dict:
        """
        Resume a paused query with a human decision.
        """
        graph = cls.get_graph()

        config = {
            "configurable": {
                "thread_id": conversation_id,
            },
            "metadata": {
                "application": "ProcureOps",
                "conversation_id": conversation_id,
            },
            "tags": [
                "procureops",
                "agent",
                "hitl",
            ],
        }

        result = await graph.ainvoke(
            Command(
                resume={
                    "decision": decision.upper(),
                    "user_id": user_id,
                }
            ),
            config=config,
        )

        # Ensure status is present
        if "status" not in result:
            if result.get("error"):
                result["status"] = "error"
            elif result.get("response"):
                result["status"] = "completed"
            elif result.get("hitl_request"):
                result["status"] = "pending_approval"
            else:
                result["status"] = "completed"

        return result