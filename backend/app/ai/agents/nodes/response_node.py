from typing import Dict, Any
import logging

from app.ai.agents.state import ProcureOpsState

logger = logging.getLogger(__name__)


def response_node(state: ProcureOpsState) -> Dict[str, Any]:
    """
    Final response node - formats and returns the response.
    """
    response = state.get("response")
    error = state.get("error")
    live_data = state.get("live_data")
    sources = state.get("sources", [])
    
    # If there's an error, return error message
    if error:
        return {
            "response": f"Error: {error}",
            "sources": [],
        }
    
    # If there's already a response, return it
    if response:
        return {
            "response": response,
            "sources": sources,
        }
    
    # If there's live data but no response, format it
    if live_data:
        return {
            "response": _format_live_data_summary(live_data),
            "sources": sources,
        }
    
    # Default response
    return {
        "response": "I'm not sure how to respond to that. Please rephrase your question.",
        "sources": [],
    }


def _format_live_data_summary(live_data: Dict) -> str:
    """Format a summary of live data."""
    if not live_data:
        return "No data available."
    
    # If it's a list of items
    if isinstance(live_data, list):
        return f"Found {len(live_data)} items."
    
    # If it's a dict with a count
    if isinstance(live_data, dict):
        if "count" in live_data:
            return f"Found {live_data['count']} items."
        if "total" in live_data:
            return f"Found {live_data['total']} items."
        if "quotation_count" in live_data:
            return f"Found {live_data['quotation_count']} quotations."
        if "rfq" in live_data:
            rfq = live_data["rfq"]
            return f"Found RFQ {rfq.get('rfq_number')} - {rfq.get('title')}"
    
    return "Data retrieved successfully."