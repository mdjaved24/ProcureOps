# Purchase Request Workflow

## 1. Purpose

This document describes the purchase request workflow supported by the ProcureOps procurement application.

A purchase request is the primary starting point for initiating a procurement requirement. It represents an internal request to acquire goods or services and may proceed through policy evaluation, approval workflows, modification requests, resubmission, and eventual approval or rejection.

This document explains the workflow and business rules conceptually. For current information about a specific purchase request, the application should retrieve live transactional data from the ProcureOps database.

---

# 2. Purchase Request Overview

A purchase request represents an internal business requirement for goods or services.

A purchase request typically contains:

- Purchase request number
- Request title
- Description
- Requested items
- Item quantities
- Units
- Estimated amount
- Currency
- Request creator
- Current workflow status
- Creation timestamp
- Update timestamp

The purchase request acts as the central business record for the procurement workflow.

The purchase request itself does not automatically represent authorization to purchase. Depending on the applicable procurement policy, additional approval may be required before the request can proceed.

---

# 3. Purchase Request Lifecycle

A purchase request can move through controlled workflow states.

A simplified lifecycle is:

DRAFT
↓
SUBMITTED
↓
POLICY EVALUATION
↓
APPROVAL PENDING, if approval is required
↓
APPROVED or REJECTED

If changes are requested:

CHANGES_REQUESTED
↓
REQUESTER MODIFIES REQUEST
↓
RESUBMITTED
↓
POLICY EVALUATION
↓
NEW APPROVAL CYCLE, if required

The exact next state depends on the applicable business rules and procurement policy.

---

# 4. Purchase Request Creation

A purchase request is initially created by an authorized user.

During creation, the requester provides the relevant procurement requirement and item information.

Typical information includes:

- Title
- Description
- Requested items
- Quantities
- Units
- Estimated amount
- Currency

The application validates the purchase request before allowing it to enter the procurement workflow.

Validation may include:

- Required fields
- Valid quantities
- Valid estimated amount
- Valid item information
- Authorization checks

After successful validation, the purchase request becomes available for submission.

---

# 5. Draft State

The DRAFT state represents a purchase request that is still being prepared.

While a purchase request is in the DRAFT state, the requester may update information according to application authorization rules.

Typical modifications may include:

- Updating the title
- Updating the description
- Updating item information
- Updating quantities
- Updating the estimated amount

A draft purchase request has not yet completed policy evaluation or approval processing.

---

# 6. Purchase Request Submission

Submission begins the controlled procurement workflow.

When a purchase request is submitted, the application evaluates the request according to applicable procurement rules.

The workflow may determine whether the purchase request:

- Requires approval
- Requires one or more approval steps
- Can proceed without approval

Policy evaluation should use the relevant request information at the time of submission.

For example, the estimated amount of a purchase request may influence which approval requirements apply.

---

# 7. Policy Evaluation

ProcureOps uses procurement policies to determine the workflow required for a purchase request.

A policy evaluation may consider request attributes such as:

- Estimated amount
- Currency
- Other policy conditions supported by the system

The result of policy evaluation determines the next workflow action.

For example:

Purchase Request
↓
Policy Evaluation
↓
Approval Required?
↓
Yes → Create Approval Workflow
No → Approve Request

Policy evaluation ensures that workflow requirements are determined consistently.

---

# 8. Approval Required

If the applicable procurement policy requires approval, the purchase request enters an approval workflow.

The application creates an approval record associated with the purchase request.

The approval workflow may contain one or more approval steps.

Each approval step can contain:

- Required role
- Approval sequence
- Current step status
- Decision maker
- Decision timestamp
- Decision comments

The purchase request remains in an approval-related workflow state until the approval process is completed.

---

# 9. Sequential Approval Processing

Approval steps are processed according to their configured sequence.

Example:

Sequence 1
Procurement Manager
↓
Sequence 2
Finance Manager
↓
Sequence 3
Senior Approver

A later approval step should not be actionable while an earlier step remains incomplete.

For example, a Finance Manager should not approve sequence 2 while sequence 1 is still pending.

Sequential processing helps ensure that the configured approval hierarchy is respected.

---

# 10. Approval Decision: Approve

An authorized approver may approve an assigned approval step.

When an approval step is approved:

1. The approval step status is updated to APPROVED.
2. The approving user is recorded.
3. The decision timestamp is recorded.
4. Optional comments may be stored.
5. The workflow evaluates whether additional approval steps remain.

If additional approval steps remain, the next eligible step becomes actionable.

If no approval steps remain, the overall approval is marked as APPROVED.

The associated purchase request may then transition to APPROVED.

---

# 11. Approval Decision: Reject

An authorized approver may reject an approval step.

When an approval step is rejected:

1. The approval step status becomes REJECTED.
2. The decision maker is recorded.
3. The decision timestamp is recorded.
4. Decision comments may be stored.
5. The overall approval is marked as REJECTED.
6. The associated purchase request transitions to REJECTED.

A rejected purchase request does not continue through the normal approval workflow.

---

# 12. Approval Decision: Request Changes

An approver may request changes when the purchase request requires modification before it can be approved.

When changes are requested:

1. The approval step is marked as CHANGES_REQUESTED.
2. The decision maker is recorded.
3. The decision timestamp is recorded.
4. Comments explaining the requested changes may be recorded.
5. The overall approval is marked as CHANGES_REQUESTED.
6. The purchase request transitions to CHANGES_REQUESTED.

The purchase request can then be modified by the appropriate requester.

---

# 13. Purchase Request Modification After Changes Requested

A purchase request in the CHANGES_REQUESTED state may be updated to address the feedback provided during the approval process.

The requester may modify relevant information such as:

- Title
- Description
- Requested items
- Quantity
- Estimated amount
- Other editable procurement information

The purpose of modification is to address the issues identified by the approver.

The request should not continue using the previous active approval cycle after significant changes are made.

---

# 14. Purchase Request Resubmission

Resubmission occurs after a purchase request in CHANGES_REQUESTED has been modified.

Resubmission is an important workflow boundary because the updated purchase request may no longer represent the same information that was previously reviewed.

The resubmission process includes:

1. Validate that the purchase request is eligible for resubmission.
2. Cancel or close the previous active approval cycle.
3. Prevent old pending approval steps from remaining actionable.
4. Re-evaluate the updated purchase request against procurement policies.
5. Determine whether approval is required.
6. Create a new approval cycle if required.
7. Transition the purchase request according to the result of the policy evaluation.
8. Record the resubmission in the audit log.

---

# 15. Previous Approval Cancellation During Resubmission

When a purchase request is resubmitted, previous active approvals must not remain actionable.

An old approval that was in an active state such as:

- PENDING
- CHANGES_REQUESTED

may be explicitly marked as CANCELLED.

Pending approval steps associated with the cancelled approval may be marked as SKIPPED.

This ensures that users cannot make decisions on an outdated approval cycle.

The historical approval record remains available for audit and workflow traceability.

Example:

Approval Cycle 1

Approval Status: CHANGES_REQUESTED
↓
Purchase Request Modified
↓
Resubmission

Approval Cycle 1
Status: CANCELLED

Pending Steps
Status: SKIPPED

↓
New Policy Evaluation
↓
Approval Cycle 2, if required

This design preserves historical records while ensuring that only the latest applicable workflow remains active.

---

# 16. New Approval Cycle

After resubmission, the updated purchase request is evaluated again.

A new approval workflow may be created based on the applicable policy.

The new approval cycle is independent of the previous approval cycle.

For example:

Previous Approval:

Approval ID: 90
Status: CANCELLED

New Approval:

Approval ID: 101
Status: PENDING

The new approval steps begin from their configured sequence.

Example:

Sequence 1
↓
Sequence 2
↓
Sequence 3

Approval decisions from a previous cycle do not automatically apply to the new cycle.

---

# 17. Resubmission Without Approval Requirement

After the purchase request is updated, the policy evaluation may determine that approval is no longer required.

For example, a change to the estimated amount may cause the purchase request to fall below a policy threshold.

In this scenario:

1. The previous approval cycle is cancelled.
2. The updated request is evaluated again.
3. No approval steps are created.
4. The purchase request proceeds according to the policy result.

The application should not create unnecessary approval records when the applicable policy does not require approval.

---

# 18. Purchase Request Approval

A purchase request becomes approved when all required approval steps have been successfully completed.

The approval process is complete when:

- No required approval steps remain pending.
- All required approval steps have been approved.
- The overall approval status is APPROVED.

The associated purchase request then transitions to APPROVED.

An approved purchase request can proceed to subsequent procurement activities such as RFQ creation and vendor quotation collection, depending on the application's business workflow.

---

# 19. Invalid Workflow Actions

The application should prevent invalid workflow transitions.

Examples include:

- Resubmitting a purchase request that is not in CHANGES_REQUESTED.
- Approving an approval step that has already been decided.
- Rejecting a step that is no longer pending.
- Deciding a later approval step before earlier required steps are approved.
- Acting on a cancelled approval.
- Acting on an outdated approval step after resubmission.

These restrictions help maintain workflow consistency.

---

# 20. Concurrency and Workflow Integrity

Approval workflows can involve multiple users acting on the same records.

The system should protect workflow operations against concurrent modification.

For critical approval decisions, the application may lock the relevant approval step and approval record during processing.

This prevents scenarios where multiple users attempt to make conflicting decisions simultaneously.

Workflow integrity ensures that:

- An approval step cannot be decided twice.
- Sequential approval rules are enforced.
- Approval status is calculated consistently.
- Purchase request status remains synchronized with the approval result.

---

# 21. Audit Logging

Important purchase request workflow actions should be recorded in the audit log.

Relevant audit events may include:

- Purchase request created
- Purchase request updated
- Purchase request submitted
- Purchase request status changed
- Approval step approved
- Approval step rejected
- Changes requested
- Approval status changed
- Purchase request resubmitted
- Previous approval cancelled

Audit records can include:

- Actor type
- Actor identifier
- Action
- Resource type
- Resource identifier
- Previous state
- New state
- Metadata
- Timestamp

Audit logging supports accountability, debugging, and workflow traceability.

---

# 22. Workflow Summary

The normal purchase request workflow can be represented as:

DRAFT
↓
SUBMITTED
↓
POLICY EVALUATION
↓
Approval Required?
├── No → APPROVED
│
└── Yes
      ↓
APPROVAL PENDING
      ↓
Approval Decision
      │
      ├── APPROVE
      │      ↓
      │   Next Step
      │      ↓
      │   All Steps Approved
      │      ↓
      │   APPROVED
      │
      ├── REJECT
      │      ↓
      │   REJECTED
      │
      └── REQUEST CHANGES
             ↓
      CHANGES_REQUESTED
             ↓
      Request Modified
             ↓
        RESUBMISSION
             ↓
      Cancel Old Approval
             ↓
      Re-evaluate Policy
             ↓
      New Approval Cycle, if required

---

# 23. AI Usage Guidelines

The AI assistant may use this knowledge to explain:

- How purchase requests work.
- Why approval may be required.
- How sequential approval works.
- What happens after rejection.
- What happens when changes are requested.
- How resubmission works.
- Why old approvals are cancelled.
- How policy evaluation affects a purchase request.

However, questions about live purchase request information should be answered using authorized application tools.

Examples of conceptual questions suitable for retrieval include:

- What happens when changes are requested?
- Why is an old approval cancelled after resubmission?
- How does sequential approval work?

Examples of transactional questions requiring live application data include:

- What is the status of my purchase request?
- Who is currently required to approve PR-101?
- Why is my request still pending?
- Which approval step is currently pending?

The AI system should distinguish between explanatory knowledge and live transactional data to ensure accurate and reliable responses.