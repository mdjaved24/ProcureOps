#!/usr/bin/env python
"""
Test script for Operation Resolver
Run: python scripts/test_operation_resolver.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.services.operation_resolver import OperationResolver, OperationType


def test_operation_resolver():
    """Test the operation resolver with various queries."""
    
    test_cases = [
        # RFQ Operations
        ("Show me RFQs", OperationType.GET_RFQS),
        ("List all RFQs", OperationType.GET_RFQS),
        ("Show me details of RFQ-000039", OperationType.GET_RFQ_DETAILS),
        ("What is the status of RFQ-000039?", OperationType.GET_RFQ_STATUS),
        ("RFQ-000039 details", OperationType.GET_RFQ_DETAILS),
        
        # Quotation Operations
        ("Show me quotations", OperationType.GET_QUOTATIONS),
        ("What are the existing quotations?", OperationType.GET_QUOTATIONS),
        ("Compare quotations for RFQ-000039", OperationType.COMPARE_QUOTATIONS),
        ("Approve quotation QT-000030", OperationType.APPROVE_QUOTATION),
        ("Reject quotation QT-000030", OperationType.REJECT_QUOTATION),
        ("Show me QT-000030", OperationType.GET_QUOTATION_DETAILS),
        
        # Vendor Operations
        ("Show me vendors", OperationType.SEARCH_VENDORS),
        ("Show vendor details", OperationType.GET_VENDOR),
        ("Search for ABC Supplies", OperationType.SEARCH_VENDORS),
        ("Find vendor ABC Supplies", OperationType.SEARCH_VENDORS),
        
        # Procurement Operations
        ("Show me procurement requests", OperationType.GET_PROCUREMENT_REQUESTS),
        ("Show details of PR-000001", OperationType.GET_PROCUREMENT_REQUEST_DETAILS),
        
        # Approval Operations
        ("Show me pending approvals", OperationType.GET_APPROVALS),
        
        # Help
        ("Help", OperationType.HELP),
        ("What can you do?", OperationType.HELP),
    ]
    
    print("=" * 60)
    print("TESTING OPERATION RESOLVER")
    print("=" * 60)
    
    previous_context = {}
    
    for query, expected in test_cases:
        result = OperationResolver.resolve(query, previous_context)
        operation = result.get("operation")
        entities = result.get("entities", {})
        confidence = result.get("confidence", 0.0)
        
        status = "✅" if operation == expected else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Expected: {expected}")
        print(f"   Got: {operation} (confidence: {confidence:.2f})")
        if entities:
            print(f"   Entities: {entities}")
        print()
        
        # Update context for follow-up tests
        previous_context["last_operation"] = operation
        previous_context["entities"] = entities
    
    # Test follow-up with NO context (separate run with fresh context)
    print("=" * 60)
    print("FOLLOW-UP TESTS (NO CONTEXT)")
    print("=" * 60)
    
    followup_cases = [
        ("Show it", OperationType.UNKNOWN),
        ("Tell me more", OperationType.UNKNOWN),
    ]
    
    # RESET context for follow-up tests
    previous_context = {}
    
    for query, expected in followup_cases:
        result = OperationResolver.resolve(query, previous_context)
        operation = result.get("operation")
        is_follow_up = result.get("is_follow_up", False)
        confidence = result.get("confidence", 0.0)
        
        status = "✅" if operation == expected else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Expected: {expected}")
        print(f"   Got: {operation} (confidence: {confidence:.2f})")
        print(f"   Is follow-up: {is_follow_up}")
        print()


def test_entity_extraction():
    """Test entity extraction."""
    from app.ai.mcp.tools.entity_extractor import EntityExtractor
    
    print("=" * 60)
    print("TESTING ENTITY EXTRACTION")
    print("=" * 60)
    
    test_cases = [
        ("Show me RFQ-000039", "rfq_number", "RFQ-000039"),
        ("Approve QT-000030", "quotation_number", "QT-000030"),
        ("Search for ABC Supplies", "vendor_search", "ABC Supplies"),
        ("Show details of PR-000001", "pr_number", "PR-000001"),
    ]
    
    for query, entity_type, expected in test_cases:
        entities = EntityExtractor.extract_all(query)
        actual = entities.get(entity_type)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   {entity_type}: {actual} (expected: {expected})")
        print()


if __name__ == "__main__":
    test_operation_resolver()
    test_entity_extraction()