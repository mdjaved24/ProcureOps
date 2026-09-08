"""
ProcureOps database seed script.

Seeds:
- Departments
- Permissions
- Roles
- Role permissions
- Users
- Policies
- Policy rules

Common password for seeded users:
    ProcureOps@123

Run from backend:
    python -m scripts.seed_database
"""

from datetime import datetime

from app.core.database import SessionLocal
from app.models.identity.department import Department
from app.models.identity.permission import Permission
from app.models.identity.role import Role
from app.models.identity.user import User
from app.models.policy.policy import Policy
from app.models.policy.policy_rule import PolicyRule


# ---------------------------------------------------------------------------
# Common password
# ---------------------------------------------------------------------------

COMMON_PASSWORD_HASH = (
    "$2b$12$J/MIKeWs7o7FHlIBTU7ou.Tqq5X2P4WrXWhB1XbA0ps1qChXVgEpO"
)


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    {
        "id": 1,
        "name": "Procurement",
        "description": "Procurement department",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Finance",
        "description": "Finance department",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "Legal",
        "description": "Legal department",
        "is_active": True,
    },
    {
        "id": 4,
        "name": "Information Security",
        "description": "Information security department",
        "is_active": True,
    },
    {
        "id": 5,
        "name": "IT",
        "description": "Information technology department",
        "is_active": True,
    },
    {
        "id": 6,
        "name": "Operations",
        "description": "Operations and logistics department",
        "is_active": True,
    },
    {
        "id": 7,
        "name": "Sales",
        "description": "Sales and business development",
        "is_active": True,
    },
    {
        "id": 8,
        "name": "Marketing",
        "description": "Marketing and communications",
        "is_active": True,
    },
    {
        "id": 9,
        "name": "Research & Development",
        "description": "R&D and innovation",
        "is_active": True,
    },
    {
        "id": 10,
        "name": "Customer Support",
        "description": "Customer service and support",
        "is_active": True,
    },
    {
        "id": 13,
        "name": "Quality Assurance",
        "description": "Quality assurance and testing",
        "is_active": True,
    },
    {
        "id": 14,
        "name": "Supply Chain",
        "description": "Supply chain and logistics",
        "is_active": True,
    },
    {
        "id": 15,
        "name": "Others",
        "description": "Other departments not listed",
        "is_active": True,
    },
]


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

PERMISSIONS = [
    (1, "procurement:create", "Create procurement requests"),
    (2, "procurement:read", "Read procurement requests"),
    (3, "procurement:update", "Update procurement requests"),
    (4, "procurement:submit", "Submit procurement requests"),
    (5, "procurement:cancel", "Cancel procurement requests"),
    (6, "vendor:create", "Create vendors"),
    (7, "vendor:read", "Read vendor information"),
    (8, "vendor:update", "Update vendor information"),
    (9, "vendor:approve", "Approve vendors"),
    (10, "contract:create", "Create contracts"),
    (11, "contract:read", "Read contracts"),
    (12, "contract:update", "Update contracts"),
    (13, "contract:approve", "Approve contracts"),
    (14, "approval:read", "Read approval requests"),
    (15, "approval:approve", "Approve approval requests"),
    (16, "approval:reject", "Reject approval requests"),
    (17, "approval:delegate", "Delegate approval requests"),
    (18, "approval:escalate", "Escalate approval requests"),
    (19, "policy:read", "Read procurement policies"),
    (20, "policy:create", "Create policies"),
    (21, "policy:update", "Update policies"),
    (22, "workflow:read", "Read workflows"),
    (23, "workflow:execute", "Execute workflows"),
    (24, "workflow:resume", "Resume paused workflows"),
    (25, "audit:read", "Read audit logs"),
    (26, "admin:users", "Manage users"),
    (27, "admin:roles", "Manage roles"),
    (28, "admin:permissions", "Manage permissions"),
    (29, "rfq:create", "Create RFQs"),
    (30, "rfq:read", "Read RFQs"),
    (31, "rfq:update", "Update RFQs"),
    (32, "quotation:read", "Read quotations"),
    (33, "quotation:submit", "Submit quotations"),
    (34, "procurement:review", "Review submitted procurement requests"),
    (35, "policy:approve", "Approve policies"),
    (36, "policy:execute", "Execute policies"),
    (37, "rfq:close", "Close RFQs"),
    (38, "rfq:cancel", "Cancel RFQs"),
    (39, "vendor:block", "Block vendors"),
    (40, "vendor:unblock", "Unblock vendors"),
    (41, "approval:request_changes", "Request changes on approvals"),
    (42, "approval:review", "Review approvals"),
    (43, "quotation:update", "Update quotations"),
    (44, "quotation:withdraw", "Withdraw quotations"),
    (45, "vendor:portal_access", "Access vendor portal"),
    (46, "vendor:view_rfqs", "View RFQs assigned to vendor"),
    (47, "vendor:submit_quotation", "Submit quotations for RFQs"),
]


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

ROLES = [
    {
        "id": 1,
        "name": "EMPLOYEE",
        "description": "Employee who creates procurement requests",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "PROCUREMENT_ANALYST",
        "description": "Procurement analyst",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "PROCUREMENT_MANAGER",
        "description": "Procurement manager",
        "is_active": True,
    },
    {
        "id": 4,
        "name": "PROCUREMENT_HEAD",
        "description": "Head of procurement",
        "is_active": True,
    },
    {
        "id": 5,
        "name": "FINANCE_OFFICER",
        "description": "Finance officer",
        "is_active": True,
    },
    {
        "id": 6,
        "name": "LEGAL_OFFICER",
        "description": "Legal officer",
        "is_active": True,
    },
    {
        "id": 7,
        "name": "SECURITY_OFFICER",
        "description": "Security officer",
        "is_active": True,
    },
    {
        "id": 8,
        "name": "COMPLIANCE_OFFICER",
        "description": "Compliance officer",
        "is_active": True,
    },
    {
        "id": 9,
        "name": "CFO",
        "description": "Chief Financial Officer",
        "is_active": True,
    },
    {
        "id": 10,
        "name": "AUDITOR",
        "description": "Auditor",
        "is_active": True,
    },
    {
        "id": 11,
        "name": "ADMIN",
        "description": "System administrator",
        "is_active": True,
    },
    {
        "id": 12,
        "name": "VENDOR",
        "description": "Vendor user with portal access",
        "is_active": True,
    },
]


# ---------------------------------------------------------------------------
# Role -> Permission mappings
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS = {
    1: [
        1, 2, 3, 4, 5
    ],

    2: [
        1, 2, 3, 4, 7, 11, 14, 19,
        22, 29, 30, 32, 34
    ],

    3: [
        1, 2, 3, 4, 7, 9, 11,
        14, 15, 16, 17, 18, 19,
        22, 23, 29, 30, 31, 32,
        34, 37, 38
    ],

    4: [
        2, 3, 4, 7, 9, 11, 13,
        14, 15, 16, 17, 18, 19,
        22, 23, 24, 29, 30, 31,
        32, 34, 37, 38
    ],

    5: [
        2, 7, 11, 14, 15, 16,
        19, 22, 30, 32
    ],

    6: [
        2, 10, 11, 12, 13, 14,
        15, 16, 19, 22, 30, 32
    ],

    7: [
        2, 11, 14, 15, 16, 19,
        22, 30, 32
    ],

    8: [
        2, 7, 11, 14, 15, 16,
        19, 22, 25, 30, 32
    ],

    9: [
        2, 7, 11, 14, 15, 16,
        18, 19, 22, 30, 32
    ],

    10: [
        2, 7, 11, 14, 19,
        22, 25, 30, 32
    ],

    11: list(range(1, 48)),

    12: [
        30, 32, 33, 45, 46, 47
    ],
}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

USERS = [
    {
        "id": 1,
        "full_name": "Md Javed",
        "email": "mdjav077@gmail.com",
        "phone": "9142450358",
        "role_id": 1,
        "department_id": 1,
        "is_active": True,
    },
    {
        "id": 2,
        "full_name": "John Doe",
        "email": "johndoe@gmail.com",
        "phone": "7858684853",
        "role_id": 1,
        "department_id": 1,
        "is_active": True,
    },
    {
        "id": 3,
        "full_name": "Employee User",
        "email": "employee@procureops.example",
        "phone": "9000000001",
        "role_id": 1,
        "department_id": 6,
        "is_active": True,
    },
    {
        "id": 4,
        "full_name": "Procurement Analyst",
        "email": "analyst@procureops.example",
        "phone": "9000000002",
        "role_id": 2,
        "department_id": 1,
        "is_active": True,
    },
    {
        "id": 5,
        "full_name": "Procurement Manager",
        "email": "manager@procureops.example",
        "phone": "9000000003",
        "role_id": 3,
        "department_id": 1,
        "is_active": True,
    },
    {
        "id": 6,
        "full_name": "Procurement Head",
        "email": "head@procureops.example",
        "phone": "9000000004",
        "role_id": 4,
        "department_id": 1,
        "is_active": True,
    },
    {
        "id": 7,
        "full_name": "Finance Officer",
        "email": "finance@procureops.example",
        "phone": "9000000005",
        "role_id": 5,
        "department_id": 2,
        "is_active": True,
    },
    {
        "id": 8,
        "full_name": "Legal Officer",
        "email": "legal@procureops.example",
        "phone": "9000000006",
        "role_id": 6,
        "department_id": 3,
        "is_active": True,
    },
    {
        "id": 9,
        "full_name": "Security Officer",
        "email": "security@procureops.example",
        "phone": "9000000007",
        "role_id": 7,
        "department_id": None,
        "is_active": True,
    },
    {
        "id": 10,
        "full_name": "Compliance Officer",
        "email": "compliance@procureops.example",
        "phone": "9000000008",
        "role_id": 8,
        "department_id": 5,
        "is_active": True,
    },
    {
        "id": 11,
        "full_name": "Chief Financial Officer",
        "email": "cfo@procureops.example",
        "phone": "9000000009",
        "role_id": 9,
        "department_id": 2,
        "is_active": True,
    },
    {
        "id": 12,
        "full_name": "Auditor User",
        "email": "auditor@procureops.example",
        "phone": "9000000010",
        "role_id": 10,
        "department_id": None,
        "is_active": True,
    },
    {
        "id": 13,
        "full_name": "System Administrator",
        "email": "admin@procureops.example",
        "phone": "9000000011",
        "role_id": 11,
        "department_id": None,
        "is_active": True,
    },
    {
        "id": 66,
        "full_name": "ABC Supplier",
        "email": "vendor@abc.com",
        "phone": "1234567890",
        "role_id": 12,
        "department_id": None,
        "is_active": True,
    },
    {
        "id": 67,
        "full_name": "TechMech Solutions",
        "email": "techmech@gmail.com",
        "phone": "1234567890",
        "role_id": 12,
        "department_id": None,
        "is_active": True,
    },
]


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------

POLICIES = [
    {
        "id": 1,
        "policy_code": "PROCUREMENT-001",
        "name": "Enterprise Procurement Approval Policy",
        "description": (
            "Defines mandatory approval controls based on procurement "
            "value and risk characteristics."
        ),
        "version": "2.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-25 11:30:59.833589+05:30",
        "updated_at": "2026-08-26 19:46:27.423226+05:30",
    },
    {
        "id": 3,
        "policy_code": "PROCUREMENT-001-d41f2d75",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:52:28.436033+05:30",
        "updated_at": "2026-08-29 00:52:28.436033+05:30",
    },
    {
        "id": 5,
        "policy_code": "PROCUREMENT-001-951490e6",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.709682+05:30",
        "updated_at": "2026-08-29 00:54:04.709682+05:30",
    },
    {
        "id": 6,
        "policy_code": "PROCUREMENT-001-4cf899a4",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.827917+05:30",
        "updated_at": "2026-08-29 00:54:04.827917+05:30",
    },
    {
        "id": 7,
        "policy_code": "PROCUREMENT-001-451a9c67",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.859902+05:30",
        "updated_at": "2026-08-29 00:54:04.859902+05:30",
    },
    {
        "id": 8,
        "policy_code": "PROCUREMENT-001-6c4b5b50",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.889434+05:30",
        "updated_at": "2026-08-29 00:54:04.889434+05:30",
    },
    {
        "id": 9,
        "policy_code": "PROCUREMENT-001-b7caf191",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.916991+05:30",
        "updated_at": "2026-08-29 00:54:04.916991+05:30",
    },
    {
        "id": 10,
        "policy_code": "PROCUREMENT-001-3fa0ed9d",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.946845+05:30",
        "updated_at": "2026-08-29 00:54:04.946845+05:30",
    },
    {
        "id": 11,
        "policy_code": "PROCUREMENT-001-dc81369e",
        "name": "Test Resubmission Policy",
        "description": "Policy used for purchase request resubmission tests",
        "version": "1.0",
        "is_active": True,
        "effective_from": None,
        "created_at": "2026-08-29 00:54:04.991845+05:30",
        "updated_at": "2026-08-29 00:54:04.991845+05:30",
    },
]


# ---------------------------------------------------------------------------
# Policy rules
# ---------------------------------------------------------------------------

POLICY_RULES = [
    {
        "id": 1,
        "policy_id": 1,
        "rule_code": "PROCUREMENT-VALUE-001",
        "name": "High Value Procurement",
        "description": (
            "Procurement requests above INR 25 lakh require "
            "Procurement Head approval."
        ),
        "priority": 100,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "value": 2500000,
            "operator": "GREATER_THAN",
        },
        "action": {
            "role": "PROCUREMENT_HEAD",
            "type": "REQUIRE_APPROVAL",
        },
    },
    {
        "id": 2,
        "policy_id": 1,
        "rule_code": "PROCUREMENT-VALUE-002",
        "name": "Executive Financial Approval",
        "description": (
            "Procurement requests above INR 50 lakh require CFO approval."
        ),
        "priority": 90,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "value": 5000000,
            "operator": "GREATER_THAN",
        },
        "action": {
            "role": "CFO",
            "type": "REQUIRE_APPROVAL",
        },
    },
    {
        "id": 3,
        "policy_id": 1,
        "rule_code": "PROCUREMENT-SECURITY-001",
        "name": "Restricted Data Processing",
        "description": (
            "Procurement involving restricted data requires "
            "Security Officer approval."
        ),
        "priority": 80,
        "is_active": True,
        "condition": {
            "field": "data_classification",
            "value": "RESTRICTED",
            "operator": "EQUALS",
        },
        "action": {
            "role": "SECURITY_OFFICER",
            "type": "REQUIRE_APPROVAL",
        },
    },
    {
        "id": 4,
        "policy_id": 3,
        "rule_code": "PROC-001",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 5,
        "policy_id": 3,
        "rule_code": "PROC-002",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 7,
        "policy_id": 5,
        "rule_code": "PROC-001-83748e55",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 8,
        "policy_id": 5,
        "rule_code": "PROC-002-83748e55",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 9,
        "policy_id": 6,
        "rule_code": "PROC-001-d9c7877b",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 10,
        "policy_id": 6,
        "rule_code": "PROC-002-d9c7877b",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 11,
        "policy_id": 7,
        "rule_code": "PROC-001-dbd73386",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 12,
        "policy_id": 7,
        "rule_code": "PROC-002-dbd73386",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 13,
        "policy_id": 8,
        "rule_code": "PROC-001-c139d28b",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 14,
        "policy_id": 8,
        "rule_code": "PROC-002-c139d28b",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 15,
        "policy_id": 9,
        "rule_code": "PROC-001-a000cc11",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 16,
        "policy_id": 9,
        "rule_code": "PROC-002-a000cc11",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 17,
        "policy_id": 10,
        "rule_code": "PROC-001-b3eacfda",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 18,
        "policy_id": 10,
        "rule_code": "PROC-002-b3eacfda",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
    {
        "id": 19,
        "policy_id": 11,
        "rule_code": "PROC-001-f7b8a76d",
        "name": "Approval required for PROCUREMENT_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 10,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 50000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "PROCUREMENT_MANAGER",
        },
    },
    {
        "id": 20,
        "policy_id": 11,
        "rule_code": "PROC-002-f7b8a76d",
        "name": "Approval required for FINANCE_MANAGER",
        "description": (
            "Require approval when estimated amount exceeds threshold"
        ),
        "priority": 20,
        "is_active": True,
        "condition": {
            "field": "estimated_amount",
            "operator": "GREATER_THAN_OR_EQUAL",
            "value": 100000.0,
        },
        "action": {
            "type": "REQUIRE_APPROVAL",
            "role": "FINANCE_MANAGER",
        },
    },
]


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

def seed_departments(db):
    for data in DEPARTMENTS:
        db.add(
            Department(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                is_active=data["is_active"],
            )
        )

    db.flush()
    print(f"✓ Seeded {len(DEPARTMENTS)} departments")


def seed_permissions(db):
    for permission_id, code, description in PERMISSIONS:
        db.add(
            Permission(
                id=permission_id,
                code=code,
                description=description,
            )
        )

    db.flush()
    print(f"✓ Seeded {len(PERMISSIONS)} permissions")


def seed_roles(db):
    for data in ROLES:
        db.add(
            Role(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                is_active=data["is_active"],
            )
        )

    db.flush()

    for role_id, permission_ids in ROLE_PERMISSIONS.items():
        role = db.get(Role, role_id)

        for permission_id in permission_ids:
            permission = db.get(Permission, permission_id)
            role.permissions.append(permission)

    db.flush()

    print(f"✓ Seeded {len(ROLES)} roles")
    print("✓ Seeded role-permission mappings")


def seed_users(db):
    for data in USERS:
        db.add(
            User(
                id=data["id"],
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                password_hash=COMMON_PASSWORD_HASH,
                role_id=data["role_id"],
                department_id=data["department_id"],
                is_active=data["is_active"],
            )
        )

    db.flush()
    print(f"✓ Seeded {len(USERS)} users")


def parse_datetime(value):
    if value is None:
        return None

    return datetime.fromisoformat(value)


def seed_policies(db):
    for data in POLICIES:
        db.add(
            Policy(
                id=data["id"],
                policy_code=data["policy_code"],
                name=data["name"],
                description=data["description"],
                version=data["version"],
                is_active=data["is_active"],
                effective_from=parse_datetime(data["effective_from"]),
                created_at=parse_datetime(data["created_at"]),
                updated_at=parse_datetime(data["updated_at"]),
            )
        )

    db.flush()

    for data in POLICY_RULES:
        db.add(
            PolicyRule(
                id=data["id"],
                policy_id=data["policy_id"],
                rule_code=data["rule_code"],
                name=data["name"],
                description=data["description"],
                priority=data["priority"],
                is_active=data["is_active"],
                condition=data["condition"],
                action=data["action"],
            )
        )

    db.flush()

    print(f"✓ Seeded {len(POLICIES)} policies")
    print(f"✓ Seeded {len(POLICY_RULES)} policy rules")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    db = SessionLocal()

    try:
        print("\nStarting ProcureOps database seed...\n")

        seed_departments(db)
        seed_permissions(db)
        seed_roles(db)
        seed_users(db)
        seed_policies(db)

        db.commit()

        print("\n========================================")
        print("ProcureOps database seeded successfully")
        print("========================================")
        print(f"Departments : {len(DEPARTMENTS)}")
        print(f"Permissions : {len(PERMISSIONS)}")
        print(f"Roles       : {len(ROLES)}")
        print(f"Users       : {len(USERS)}")
        print(f"Policies    : {len(POLICIES)}")
        print(f"Policy Rules: {len(POLICY_RULES)}")
        print("----------------------------------------")
        print("Common password: ProcureOps@123")
        print("========================================\n")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()