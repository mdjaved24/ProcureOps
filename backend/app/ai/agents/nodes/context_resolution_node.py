from app.ai.agents.state import ProcureOpsState
from app.ai.mcp.tools.entity_extractor import EntityExtractor
import re
import logging

logger = logging.getLogger(__name__)


def context_resolution_node(
    state: ProcureOpsState,
) -> dict:
    """
    Resolve context from the user query and conversation state.
    Extracts entities and maintains conversation context using unified EntityExtractor.
    """
    user_query = state.get("user_query", "")
    operation = state.get("operation")
    
    conversation_context = state.get(
        "conversation_context",
        {},
    )
    
    updates = {}
    
    # ============================================================
    # STEP 1: Extract ALL entities using unified extractor
    # ============================================================
    
    entities = EntityExtractor.extract_all(user_query)
    logger.info(f"Extracted entities: {entities}")
    
    # ============================================================
    # STEP 2: Extract RFQ from current query
    # ============================================================
    
    extracted_rfq_number = entities.get("rfq_number")
    extracted_rfq_id = entities.get("rfq_id")
    
    if extracted_rfq_number:
        updates["rfq_number"] = extracted_rfq_number
        if extracted_rfq_id:
            updates["rfq_id"] = extracted_rfq_id
        updates["conversation_context"] = {
            **conversation_context,
            "active_rfq": extracted_rfq_number,
        }
        logger.info(f"Extracted RFQ: {extracted_rfq_number} (ID: {extracted_rfq_id})")
    
    elif conversation_context.get("active_rfq"):
        updates["rfq_number"] = conversation_context["active_rfq"]
        logger.info(f"Using active RFQ from context: {conversation_context['active_rfq']}")
    
    elif state.get("rfq_number"):
        updates["rfq_number"] = state["rfq_number"]
        logger.info(f"Using RFQ from state: {state['rfq_number']}")
    
    # ============================================================
    # STEP 3: Extract Quotation from current query
    # ============================================================
    
    extracted_quotation_id = entities.get("quotation_id")
    extracted_quotation_number = entities.get("quotation_number")
    
    if extracted_quotation_id:
        updates["quotation_id"] = extracted_quotation_id
        logger.info(f"Extracted Quotation ID: {extracted_quotation_id}")
    
    if extracted_quotation_number:
        updates["quotation_number"] = extracted_quotation_number
        updates["conversation_context"] = {
            **conversation_context,
            "active_quotation": extracted_quotation_number,
        }
        logger.info(f"Extracted Quotation Number: {extracted_quotation_number}")
    
    # If quotation_id is extracted but not number, try to get number from ID
    if extracted_quotation_id and not extracted_quotation_number:
        qt_number = f"QT-{str(extracted_quotation_id).zfill(6)}"
        updates["quotation_number"] = qt_number
        updates["conversation_context"] = {
            **conversation_context,
            "active_quotation": qt_number,
        }
        logger.info(f"Generated Quotation Number from ID: {qt_number}")
    
    # Check if operation contains quotation info
    if operation and not updates.get("quotation_id"):
        qt_match = re.search(r'QT[-\s\u2011_]*(\d+)', operation, re.IGNORECASE)
        if qt_match:
            qt_id = int(qt_match.group(1))
            qt_number = f"QT-{qt_match.group(1).zfill(6)}"
            updates["quotation_id"] = qt_id
            updates["quotation_number"] = qt_number
            updates["conversation_context"] = {
                **conversation_context,
                "active_quotation": qt_number,
            }
            logger.info(f"Extracted Quotation from operation: {qt_number} (ID: {qt_id})")
    
    # If still no quotation, check conversation context
    if not updates.get("quotation_id") and conversation_context.get("active_quotation"):
        qt_number = conversation_context["active_quotation"]
        qt_match = re.search(r'(\d+)', qt_number)
        if qt_match:
            updates["quotation_id"] = int(qt_match.group(1))
            updates["quotation_number"] = qt_number
            logger.info(f"Using quotation from context: {qt_number}")
    
    # ============================================================
    # STEP 4: Extract Vendor
    # ============================================================
    
    vendor_id = entities.get("vendor_id")
    vendor_code = entities.get("vendor_code")
    vendor_status = entities.get("vendor_status")
    vendor_search = entities.get("vendor_search")
    vendor_name = entities.get("vendor_name")
    
    if vendor_id is not None:
        updates["vendor_id"] = vendor_id
        logger.info(f"Extracted Vendor ID: {vendor_id}")
    
    if vendor_code is not None:
        updates["vendor_code"] = vendor_code
        logger.info(f"Extracted Vendor Code: {vendor_code}")
    
    if vendor_status is not None:
        updates["vendor_status"] = vendor_status
        logger.info(f"Extracted Vendor Status: {vendor_status}")
    
    if vendor_search is not None:
        updates["vendor_search"] = vendor_search
        updates["vendor_name"] = vendor_search
        logger.info(f"Extracted Vendor Search: {vendor_search}")
    
    if vendor_name is not None and not vendor_search:
        updates["vendor_name"] = vendor_name
        updates["vendor_search"] = vendor_name
        logger.info(f"Extracted Vendor Name: {vendor_name}")
    
    # ============================================================
    # STEP 5: Extract Purchase Request
    # ============================================================
    
    pr_match = re.search(r'PR[-\s]*(\d+)', user_query, re.IGNORECASE)
    if pr_match:
        pr_num = pr_match.group(1)
        pr_number = f"PR-{pr_num.zfill(6)}"
        updates["purchase_request_number"] = pr_number
        updates["conversation_context"] = {
            **conversation_context,
            "active_purchase_request": pr_number,
        }
        logger.info(f"Extracted Purchase Request: {pr_number}")
    
    # ============================================================
    # STEP 6: Detect query types from entities
    # ============================================================
    
    # is_quotation_action returns a tuple (is_action, action_type)
    is_quotation_action_result = entities.get("is_quotation_action", (False, None))
    if isinstance(is_quotation_action_result, tuple):
        is_quotation_action, action_type = is_quotation_action_result
    else:
        is_quotation_action = False
        action_type = None
    
    is_rfq_list = entities.get("is_rfq_list", False)
    is_vendor_list = entities.get("is_vendor_list", False)
    is_quotation_list = entities.get("is_quotation_list", False)
    
    if is_rfq_list:
        updates["is_list_query"] = True
        updates["list_type"] = "RFQ"
        logger.info("RFQ list query detected")
    
    if is_vendor_list:
        updates["is_list_query"] = True
        updates["list_type"] = "VENDOR"
        logger.info("Vendor list query detected")
    
    if is_quotation_list:
        updates["is_list_query"] = True
        updates["list_type"] = "QUOTATION"
        logger.info("Quotation list query detected")
    
    if is_quotation_action:
        updates["is_action_query"] = True
        updates["action_type"] = action_type
        logger.info(f"Quotation action detected: {action_type}")
    
    # ============================================================
    # STEP 7: Update conversation context
    # ============================================================
    
    if operation:
        updates["conversation_context"] = {
            **updates.get("conversation_context", conversation_context),
            "last_operation": operation,
        }
    
    # Preserve existing context
    if not updates.get("conversation_context"):
        updates["conversation_context"] = conversation_context
    
    # ============================================================
    # STEP 8: Log final context
    # ============================================================
    
    logger.info(f"Final context: {updates.get('conversation_context', {})}")
    logger.info(f"RFQ: {updates.get('rfq_number')}")
    logger.info(f"Quotation: {updates.get('quotation_number')} (ID: {updates.get('quotation_id')})")
    logger.info(f"Vendor: {updates.get('vendor_name') or updates.get('vendor_id')}")
    logger.info(f"PR: {updates.get('purchase_request_number')}")
    
    return updates