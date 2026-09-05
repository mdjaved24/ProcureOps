#!/usr/bin/env python
"""
Test script for MCP Tools
Run: python scripts/test_mcp_tools.py
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.mcp.client.procureops_client import ProcureOpsMCPClient
from app.ai.mcp.tools.tool_mapper import MCPToolMapper
from app.ai.services.operation_resolver import OperationType


async def test_mcp_tools():
    """Test MCP tools."""
    
    print("=" * 60)
    print("TESTING MCP TOOLS")
    print("=" * 60)
    
    # Test listing tools
    print("\n1. Listing available tools...")
    tools = await ProcureOpsMCPClient.list_tools()
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    
    # Test tool mapping
    print("\n2. Testing tool mapping...")
    
    test_operations = [
        (OperationType.GET_RFQS, {"rfq_id": None}),
        (OperationType.GET_RFQ_DETAILS, {"rfq_id": 39}),
        (OperationType.GET_QUOTATIONS, {}),
        (OperationType.APPROVE_QUOTATION, {"quotation_id": 30}),
        (OperationType.SEARCH_VENDORS, {"vendor_search": "ABC"}),
    ]
    
    for operation, entities in test_operations:
        tool_config = MCPToolMapper.get_tool(operation, entities)
        print(f"   {operation} → {tool_config.get('tool_name')} ({tool_config.get('arguments')})")
    
    # Test actual tool calls (optional - uncomment to test)
    print("\n3. Testing actual tool calls...")
    
    # Test get_rfqs
    print("\n   Calling get_rfqs...")
    result = await ProcureOpsMCPClient.call_tool("get_rfqs", {"limit": 3})
    if result.get("success"):
        data = result.get("data", {})
        rfqs = data.get("rfqs", [])
        print(f"   ✅ Found {len(rfqs)} RFQs")
        for rfq in rfqs[:2]:
            print(f"      - {rfq.get('rfq_number')}: {rfq.get('title')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test get_quotations
    print("\n   Calling get_quotations...")
    result = await ProcureOpsMCPClient.call_tool("get_quotations", {})
    if result.get("success"):
        data = result.get("data", {})
        quotations = data.get("quotations", [])
        print(f"   ✅ Found {len(quotations)} quotations")
        for q in quotations[:2]:
            print(f"      - {q.get('quotation_number')}: {q.get('vendor_name')} - {q.get('total_amount')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())