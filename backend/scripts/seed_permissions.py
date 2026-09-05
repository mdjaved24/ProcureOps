#!/usr/bin/env python
"""
Seed Permissions and Role Permissions Script for ProcureOps

Usage:
    python scripts/seed_permissions.py

This script will:
1. Insert all permissions
2. Assign permissions to each role
3. Verify the seeding was successful

Run with --help for more options
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine

# ============================================================
# Fix Unicode for Windows Console
# ============================================================

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def checkmark(val: bool) -> str:
    """Return checkmark or cross mark based on boolean."""
    return "[✓]" if val else "[✗]"

def success_text(text: str) -> str:
    """Return text with success indicator."""
    return f"[✓] {text}"

def error_text(text: str) -> str:
    """Return text with error indicator."""
    return f"[✗] {text}"

def info_text(text: str) -> str:
    """Return text with info indicator."""
    return f"[i] {text}"

# ============================================================
# PERMISSIONS DATA
# ============================================================

PERMISSIONS = [
    # Procurement Permissions (1-5)
    {"id": 1, "code": "procurement:create", "description": "Create procurement requests"},
    {"id": 2, "code": "procurement:read", "description": "Read procurement requests"},
    {"id": 3, "code": "procurement:update", "description": "Update procurement requests"},
    {"id": 4, "code": "procurement:submit", "description": "Submit procurement requests"},
    {"id": 5, "code": "procurement:cancel", "description": "Cancel procurement requests"},
    
    # Vendor Permissions (6-9)
    {"id": 6, "code": "vendor:create", "description": "Create vendors"},
    {"id": 7, "code": "vendor:read", "description": "Read vendor information"},
    {"id": 8, "code": "vendor:update", "description": "Update vendor information"},
    {"id": 9, "code": "vendor:approve", "description": "Approve vendors"},
    
    # Contract/RFQ Permissions (10-13)
    {"id": 10, "code": "contract:create", "description": "Create contracts"},
    {"id": 11, "code": "contract:read", "description": "Read contracts"},
    {"id": 12, "code": "contract:update", "description": "Update contracts"},
    {"id": 13, "code": "contract:approve", "description": "Approve contracts"},
    
    # Approval Permissions (14-18)
    {"id": 14, "code": "approval:read", "description": "Read approval requests"},
    {"id": 15, "code": "approval:approve", "description": "Approve approval requests"},
    {"id": 16, "code": "approval:reject", "description": "Reject approval requests"},
    {"id": 17, "code": "approval:delegate", "description": "Delegate approval requests"},
    {"id": 18, "code": "approval:escalate", "description": "Escalate approval requests"},
    
    # Policy Permissions (19-21)
    {"id": 19, "code": "policy:read", "description": "Read procurement policies"},
    {"id": 20, "code": "policy:create", "description": "Create policies"},
    {"id": 21, "code": "policy:update", "description": "Update policies"},
    
    # Workflow Permissions (22-24)
    {"id": 22, "code": "workflow:read", "description": "Read workflows"},
    {"id": 23, "code": "workflow:execute", "description": "Execute workflows"},
    {"id": 24, "code": "workflow:resume", "description": "Resume paused workflows"},
    
    # Audit Permissions (25)
    {"id": 25, "code": "audit:read", "description": "Read audit logs"},
    
    # Admin Permissions (26-28)
    {"id": 26, "code": "admin:users", "description": "Manage users"},
    {"id": 27, "code": "admin:roles", "description": "Manage roles"},
    {"id": 28, "code": "admin:permissions", "description": "Manage permissions"},
    
    # RFQ Permissions (29-31)
    {"id": 29, "code": "rfq:create", "description": "Create RFQs"},
    {"id": 30, "code": "rfq:read", "description": "Read RFQs"},
    {"id": 31, "code": "rfq:update", "description": "Update RFQs"},
    
    # Quotation Permissions (32-33)
    {"id": 32, "code": "quotation:read", "description": "Read quotations"},
    {"id": 33, "code": "quotation:submit", "description": "Submit quotations"},
    
    # Additional Procurement Permissions (34)
    {"id": 34, "code": "procurement:review", "description": "Review submitted procurement requests"},
    
    # Additional Policy Permissions (35-36)
    {"id": 35, "code": "policy:approve", "description": "Approve policies"},
    {"id": 36, "code": "policy:execute", "description": "Execute policies"},
    
    # Additional RFQ Permissions (37-38)
    {"id": 37, "code": "rfq:close", "description": "Close RFQs"},
    {"id": 38, "code": "rfq:cancel", "description": "Cancel RFQs"},
    
    # Additional Vendor Permissions (39-40)
    {"id": 39, "code": "vendor:block", "description": "Block vendors"},
    {"id": 40, "code": "vendor:unblock", "description": "Unblock vendors"},
    
    # Additional Approval Permissions (41-42)
    {"id": 41, "code": "approval:request_changes", "description": "Request changes on approvals"},
    {"id": 42, "code": "approval:review", "description": "Review approvals"},
    
    # Additional Quotation Permissions (43-44)
    {"id": 43, "code": "quotation:update", "description": "Update quotations"},
    {"id": 44, "code": "quotation:withdraw", "description": "Withdraw quotations"},
]

# ============================================================
# ROLE PERMISSIONS DATA
# ============================================================

ROLE_PERMISSIONS = {
    # EMPLOYEE (Role ID: 1)
    # Employee can create, read, update, submit, and cancel their own procurement requests
    1: [
        1, 2, 3, 4, 5  # procurement:create, read, update, submit, cancel
    ],
    
    # PROCUREMENT_ANALYST (Role ID: 2)
    2: [
        1, 2, 3, 4,    # procurement:create, read, update, submit
        7,             # vendor:read
        11,            # contract:read
        14,            # approval:read
        19,            # policy:read
        22,            # workflow:read
        29, 30,        # rfq:create, rfq:read
        32,            # quotation:read
        34,            # procurement:review
    ],
    
    # PROCUREMENT_MANAGER (Role ID: 3)
    3: [
        1, 2, 3, 4,    # procurement:create, read, update, submit
        7, 9,          # vendor:read, vendor:approve
        11,            # contract:read
        14, 15, 16, 17, 18,  # approval:read, approve, reject, delegate, escalate
        19,            # policy:read
        22, 23,        # workflow:read, workflow:execute
        29, 30, 31,    # rfq:create, read, update
        32,            # quotation:read
        34,            # procurement:review
        37, 38,        # rfq:close, rfq:cancel
    ],
    
    # PROCUREMENT_HEAD (Role ID: 4)
    4: [
        2, 3, 4,       # procurement:read, update, submit
        7, 9,          # vendor:read, vendor:approve
        11, 13,        # contract:read, contract:approve
        14, 15, 16, 17, 18,  # approval:read, approve, reject, delegate, escalate
        19,            # policy:read
        22, 23, 24,    # workflow:read, execute, resume
        29, 30, 31,    # rfq:create, read, update
        32,            # quotation:read
        34,            # procurement:review
        37, 38,        # rfq:close, rfq:cancel
    ],
    
    # FINANCE_OFFICER (Role ID: 5)
    5: [
        2,             # procurement:read
        7,             # vendor:read
        11,            # contract:read
        14, 15, 16,    # approval:read, approve, reject
        19,            # policy:read
        22,            # workflow:read
        30,            # rfq:read
        32,            # quotation:read
    ],
    
    # LEGAL_OFFICER (Role ID: 6)
    6: [
        2,             # procurement:read
        10, 11, 12, 13, # contract:create, read, update, approve
        14, 15, 16,    # approval:read, approve, reject
        19,            # policy:read
        22,            # workflow:read
        30,            # rfq:read
        32,            # quotation:read
    ],
    
    # SECURITY_OFFICER (Role ID: 7)
    7: [
        2,             # procurement:read
        11,            # contract:read
        14, 15, 16,    # approval:read, approve, reject
        19,            # policy:read
        22,            # workflow:read
        30,            # rfq:read
        32,            # quotation:read
    ],
    
    # COMPLIANCE_OFFICER (Role ID: 8)
    8: [
        2,             # procurement:read
        7,             # vendor:read
        11,            # contract:read
        14, 15, 16,    # approval:read, approve, reject
        19,            # policy:read
        22,            # workflow:read
        25,            # audit:read
        30,            # rfq:read
        32,            # quotation:read
    ],
    
    # CFO (Role ID: 9)
    9: [
        2,             # procurement:read
        7,             # vendor:read
        11,            # contract:read
        14, 15, 16, 18, # approval:read, approve, reject, escalate
        19,            # policy:read
        22,            # workflow:read
        30,            # rfq:read
        32,            # quotation:read
    ],
    
    # AUDITOR (Role ID: 10)
    10: [
        2,             # procurement:read
        7,             # vendor:read
        11,            # contract:read
        14,            # approval:read
        19,            # policy:read
        22,            # workflow:read
        25,            # audit:read
        30,            # rfq:read
        32,            # quotation:read
    ],
    
    # ADMIN (Role ID: 11)
    11: [
        # Admin Permissions
        26, 27, 28,    # admin:users, roles, permissions
        
        # Procurement
        1, 2, 3, 4, 5, 34,
        
        # Vendor
        6, 7, 8, 9, 39, 40,
        
        # Contract/RFQ
        10, 11, 12, 13, 29, 30, 31, 37, 38,
        
        # Quotation
        32, 33, 43, 44,
        
        # Approval
        14, 15, 16, 17, 18, 41, 42,
        
        # Policy
        19, 20, 21, 35, 36,
        
        # Workflow
        22, 23, 24,
        
        # Audit
        25,
    ],
}

# ============================================================
# SEEDING FUNCTIONS
# ============================================================

def seed_permissions(db: Session, clear_existing: bool = False):
    """Insert all permissions."""
    
    if clear_existing:
        print(info_text("Clearing existing permissions..."))
        db.execute(text("DELETE FROM role_permissions"))
        db.execute(text("DELETE FROM permissions"))
        db.commit()
    
    print(info_text("Inserting permissions..."))
    for perm in PERMISSIONS:
        stmt = text("""
            INSERT INTO permissions (id, code, description)
            VALUES (:id, :code, :description)
            ON CONFLICT (id) DO UPDATE SET
                code = EXCLUDED.code,
                description = EXCLUDED.description
        """)
        db.execute(stmt, perm)
    
    db.commit()
    print(success_text(f"Inserted {len(PERMISSIONS)} permissions"))


def seed_role_permissions(db: Session):
    """Insert role permissions."""
    
    print(info_text("Inserting role permissions..."))
    total = 0
    
    for role_id, permission_ids in ROLE_PERMISSIONS.items():
        for perm_id in permission_ids:
            stmt = text("""
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (:role_id, :perm_id)
                ON CONFLICT (role_id, permission_id) DO NOTHING
            """)
            db.execute(stmt, {"role_id": role_id, "perm_id": perm_id})
            total += 1
    
    db.commit()
    print(success_text(f"Assigned {total} role permissions"))


def verify_seeding(db: Session):
    """Verify the seeding was successful."""
    
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    # Check total permissions
    result = db.execute(text("SELECT COUNT(*) FROM permissions"))
    perm_count = result.scalar()
    print(f"Total Permissions: {perm_count}")
    
    # Check total role permissions
    result = db.execute(text("SELECT COUNT(*) FROM role_permissions"))
    rp_count = result.scalar()
    print(f"Total Role Permissions Assigned: {rp_count}")
    
    # Check each role
    print("\nRole Permissions Summary:")
    print("-" * 60)
    
    result = db.execute(text("""
        SELECT 
            r.name AS role_name,
            r.id AS role_id,
            COUNT(rp.permission_id) AS permission_count
        FROM roles r
        LEFT JOIN role_permissions rp ON rp.role_id = r.id
        WHERE r.is_active = true
        GROUP BY r.id, r.name
        ORDER BY r.id
    """))
    
    for row in result:
        print(f"  {row.role_name:25} ({row.role_id:2}): {row.permission_count:3} permissions")
    
    # Check RFQ permissions specifically
    print("\nRFQ Permissions by Role:")
    print("-" * 60)
    
    result = db.execute(text("""
        SELECT 
            r.name AS role_name,
            CASE WHEN rp29.role_id IS NOT NULL THEN 'YES' ELSE 'NO' END AS rfq_create,
            CASE WHEN rp30.role_id IS NOT NULL THEN 'YES' ELSE 'NO' END AS rfq_read,
            CASE WHEN rp31.role_id IS NOT NULL THEN 'YES' ELSE 'NO' END AS rfq_update
        FROM roles r
        LEFT JOIN role_permissions rp29 ON rp29.role_id = r.id AND rp29.permission_id = 29
        LEFT JOIN role_permissions rp30 ON rp30.role_id = r.id AND rp30.permission_id = 30
        LEFT JOIN role_permissions rp31 ON rp31.role_id = r.id AND rp31.permission_id = 31
        WHERE r.is_active = true
        ORDER BY r.id
    """))
    
    print(f"  {'Role':25} {'Create':10} {'Read':10} {'Update':10}")
    print("  " + "-" * 55)
    for row in result:
        print(f"  {row.role_name:25} {row.rfq_create:10} {row.rfq_read:10} {row.rfq_update:10}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Seed permissions and role permissions for ProcureOps")
    parser.add_argument("--clear", action="store_true", help="Clear existing permissions before seeding")
    parser.add_argument("--verify", action="store_true", help="Only verify existing permissions, don't seed")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print(info_text("DRY RUN - No changes will be made"))
        print(f"Would insert {len(PERMISSIONS)} permissions")
        print(f"Would assign role permissions for {len(ROLE_PERMISSIONS)} roles")
        return
    
    if args.verify:
        print(info_text("Verifying existing permissions..."))
        with Session(engine) as db:
            verify_seeding(db)
        return
    
    print("=" * 60)
    print("PROCUREOPS - PERMISSIONS SEEDING")
    print("=" * 60)
    print(f"Database: {settings.database_url}")
    print()
    
    try:
        with Session(engine) as db:
            seed_permissions(db, clear_existing=args.clear)
            seed_role_permissions(db)
            verify_seeding(db)
            
        print("\n" + success_text("Seeding completed successfully!"))
        print("\nNext steps:")
        print("1. Restart the backend server")
        print("2. Clear Redis cache (if using): redis-cli flushall")
        print("3. Logout and login again to refresh permissions")
        
    except Exception as e:
        print(f"\n" + error_text(f"Error during seeding: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()