#!/usr/bin/env python
"""
Test script for Complete Agent Flow
Run: python scripts/test_agent.py
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.agents.agent_service import ProcureOpsAgentService


async def test_agent():
    """Test the complete agent flow."""
    
    print("=" * 60)
    print("TESTING COMPLETE AGENT FLOW")
    print("=" * 60)
    
    user_id = 6  # Procurement Head
    
    test_queries = [
        "Show me RFQs",
        "Show me details of RFQ-000039",
        "What are the existing quotations?",
        "Compare quotations for RFQ-000039",
        "Show me vendors",
        "Show me procurement requests",
        "Show me pending approvals",
        "Help",
    ]
    
    for query in test_queries:
        print(f"\n{'='*40}")
        print(f"Query: '{query}'")
        print(f"{'='*40}")
        
        conversation_id = f"test-{hash(query) % 10000}"
        
        result = await ProcureOpsAgentService.process_query(
            user_query=query,
            conversation_id=conversation_id,
            user_id=user_id,
        )
        
        status = result.get("status", "unknown")
        response = result.get("response", "No response")
        
        print(f"Status: {status}")
        print(f"Response: {response[:500]}..." if len(response) > 500 else f"Response: {response}")
        
        if result.get("error"):
            print(f"Error: {result.get('error')}")
        
        # Print state summary
        state = result.get("conversation_context", {})
        if state:
            print(f"Context: {state}")


if __name__ == "__main__":
    asyncio.run(test_agent())