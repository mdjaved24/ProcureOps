# Approval Workflow

## 1. Purpose

This document describes the approval workflow used in the ProcureOps procurement application.

Approval workflows provide controlled authorization before a purchase request proceeds to subsequent procurement activities. The workflow ensures that procurement requests are reviewed by authorized users according to the configured approval sequence and applicable procurement policies.

The information in this document is intended for conceptual and procedural questions. Current approval status, pending approval steps, approver assignments, and specific purchase request information should be retrieved from authorized transactional data sources.

---

# 2. Approval Workflow Overview

An approval workflow is created when a purchase request requires authorization according to an applicable procurement policy.

An approval workflow may contain:

- An overall approval record
- One or more approval steps
- Approval sequence information
- Required approver roles
- Approval status
- Decision information
- Decision timestamps
- Comments

The approval workflow represents the lifecycle of authorization associated with a purchase request.

A single purchase request may have multiple approval cycles over its lifetime, particularly when changes are requested and the purchase request is resubmitted.

---

# 3. Overall Approval Record

The overall approval record represents the status of an approval cycle.

An approval record is associated with a specific purchase request and contains the overall result of the approval process.

Typical information may include:

- Approval identifier
- Purchase request identifier
- Approval status
- Applicable policy
- Approval creation timestamp
- Completion timestamp
- Related approval steps

The overall approval status provides a high-level representation of the approval cycle.

Individual approval steps provide the detailed decisions that lead to the overall status.

---

# 4. Approval Steps

An approval workflow can contain multiple approval steps.

Each approval step represents an individual authorization requirement.

A step may contain:

- Step identifier
- Approval identifier
- Required approver role
- Approval sequence number
- Step status
- Decision maker
- Decision timestamp
- Comments

Approval steps allow the application to record individual decisions independently while maintaining an overall workflow result.

---

# 5. Approval Sequence

Approval steps may be processed sequentially.

Each step has a sequence number that determines its order.

Example:

Sequence 1
Procurement Manager

Sequence 2
Finance Manager

Sequence 3
Senior Approver

The application should enforce the configured sequence.

A step should become actionable only when all required previous steps have been successfully completed.

---

# 6. Sequential Approval Example

Consider the following workflow:

Step 1
Required Role: Procurement Manager
Status: APPROVED

↓

Step 2
Required Role: Finance Manager
Status: PENDING

↓

Step 3
Required Role: Senior Approver
Status: PENDING

In this situation:

- Step 1 has been completed.
- Step 2 is the current actionable step.
- Step 3 should not yet be actionable.

A user associated with the Senior Approver role should not be able to bypass the Finance Manager step.

This ensures that the configured approval hierarchy is respected.

---

# 7. Authorization

An approval decision should only be made by an authorized user.

Authorization may depend on:

- The user's role
- The required role for the approval step
- Whether the approval step is currently actionable
- Whether the approval workflow is active
- Whether the user is permitted to perform the decision

The application should validate authorization before changing an approval step.

The AI assistant should not independently bypass authorization controls.

---

# 8. Approval Step Status

Approval steps may have different states depending on their lifecycle.

Typical states include:

## PENDING

The approval step has not yet received a decision.

A pending step may be actionable if all required previous approval steps have been completed.

---

## APPROVED

The required approver has approved the step.

The application records:

- Approver identity
- Decision timestamp
- Optional decision comments

The workflow may then activate the next approval step.

---

## REJECTED

The approver has rejected the approval step.

A rejected step usually results in the overall approval workflow being rejected.

The associated purchase request may transition to REJECTED.

---

## CHANGES_REQUESTED

The approver requires modifications before the purchase request can continue.

The workflow is paused while the requester modifies the purchase request.

After modification, the request may be resubmitted for policy evaluation.

---

## SKIPPED

A step may be marked as skipped when it is no longer applicable.

For example, when a purchase request is resubmitted and the previous approval cycle is cancelled, pending steps from the previous workflow can be marked as SKIPPED.

Skipped steps should not be actionable.

---

# 9. Overall Approval Status

The overall approval status represents the state of the approval cycle.

Typical statuses include:

## PENDING

The approval workflow is active and requires one or more decisions.

---

## APPROVED

All required approval steps have been successfully approved.

The associated purchase request may proceed to APPROVED.

---

## REJECTED

An approval decision has rejected the request.

The associated purchase request may transition to REJECTED.

---

## CHANGES_REQUESTED

An approver has requested modifications.

The associated purchase request may transition to CHANGES_REQUESTED.

---

## CANCELLED

The approval cycle is no longer active.

Cancellation can occur when a purchase request is resubmitted and a new approval cycle must be created.

Cancelled approval workflows should not accept new approval decisions.

---

# 10. Approval Decision: Approve

When an authorized user approves the current approval step:

1. The application validates that the approval workflow is active.
2. The application validates that the step is currently actionable.
3. The application validates that the user has the required authorization.
4. The approval step status changes to APPROVED.
5. The decision maker is recorded.
6. The decision timestamp is recorded.
7. Optional comments may be recorded.
8. The application determines whether additional steps remain.

If additional approval steps remain, the next eligible step becomes actionable.

If all required steps have been approved, the overall approval status becomes APPROVED.

The associated purchase request may then transition to APPROVED.

---

# 11. Approval Decision: Reject

When an authorized user rejects an approval step:

1. The application validates authorization.
2. The application validates that the workflow is active.
3. The approval step status becomes REJECTED.
4. The decision maker is recorded.
5. The decision timestamp is recorded.
6. Decision comments may be recorded.
7. The overall approval workflow becomes REJECTED.
8. The associated purchase request may transition to REJECTED.

A rejected approval workflow should not continue to subsequent approval steps.

---

# 12. Approval Decision: Request Changes

An approver may request changes when additional information or modifications are required.

When changes are requested:

1. The approval step status becomes CHANGES_REQUESTED.
2. The decision maker is recorded.
3. The decision timestamp is recorded.
4. Comments may describe the required modifications.
5. The overall approval workflow becomes CHANGES_REQUESTED.
6. The associated purchase request becomes CHANGES_REQUESTED.

The requester can then modify the purchase request.

The request may subsequently be resubmitted.

---

# 13. Approval Workflow Resubmission

Resubmission creates a separation between an old version of the procurement request and the updated version.

A typical resubmission workflow is:

Purchase Request
Status: CHANGES_REQUESTED

↓

Requester Updates Request

↓

Previous Approval Workflow
Status: CANCELLED

↓

Old Pending Steps
Status: SKIPPED

↓

Policy Evaluation

↓

New Approval Workflow, if required

The previous approval workflow remains stored for historical and audit purposes.

However, it should no longer be possible to perform decisions on that workflow.

---

# 14. Why Approval Cycles Are Cancelled

Approval decisions are based on the state of a purchase request at a particular point in time.

If the purchase request is modified after changes are requested, previously recorded decisions may no longer apply.

For example, a purchase request may originally contain:

Estimated Amount: 100,000

After modification:

Estimated Amount: 1,000,000

The original approval requirements may no longer be sufficient.

Cancelling the previous approval cycle ensures that:

- Old decisions cannot be reused incorrectly.
- Pending approvers cannot approve outdated information.
- Policies can be evaluated against the updated request.
- A new approval workflow can be created when required.

---

# 15. Approval Policy Evaluation

Approval workflows are generally created based on policy evaluation.

A policy may define conditions such as:

- Minimum purchase amount
- Maximum purchase amount
- Required approval roles
- Approval sequence

Example:

Amount between 0 and 50,000

↓

Approval Required: No

Amount between 50,001 and 500,000

↓

Approval Required: Procurement Manager

Amount above 500,000

↓

Procurement Manager
↓
Finance Manager
↓
Senior Approver

The exact policies supported by the application depend on the configured procurement policy model.

---

# 16. Invalid Approval Actions

The application should reject invalid workflow actions.

Examples include:

- Approving a step that is already approved.
- Rejecting a completed step.
- Requesting changes on a cancelled approval.
- Approving a step from an old approval cycle.
- Acting on a skipped step.
- Approving a later sequence before earlier steps are complete.
- Performing an action without the required authorization.

These controls protect workflow integrity.

---

# 17. Concurrency Control

Approval decisions can be high-risk transactional operations.

Multiple users may attempt to interact with the same approval workflow simultaneously.

Example:

Two authorized users attempt to approve the same step at nearly the same time.

Without concurrency control, the system could:

- Record conflicting decisions.
- Process the same approval step twice.
- Incorrectly activate later workflow steps.

The application should use appropriate transaction management and database locking for critical workflow operations.

A common approach is to lock the relevant approval step during decision processing.

The application then:

1. Locks the approval step.
2. Validates its current state.
3. Validates authorization.
4. Applies the decision.
5. Updates related workflow records.
6. Creates required audit records.
7. Commits the transaction.

This helps ensure that approval decisions remain consistent.

---

# 18. Transaction Integrity

Approval operations often modify multiple records.

For example, approving a final step may update:

- The approval step
- The overall approval
- The purchase request
- The audit log

These changes should be treated as a single logical transaction.

If an unexpected failure occurs, the transaction should be rolled back.

This prevents partial workflow updates.

Example:

Approval Step → Updated

Overall Approval → Updated

Purchase Request → Failure

Without a transaction, the system could contain inconsistent data.

Using transactional processing ensures that either all required changes succeed or none of them are permanently applied.

---

# 19. Audit Logging

Approval-related actions should be recorded for traceability.

Relevant audit events may include:

- Approval workflow created
- Approval step approved
- Approval step rejected
- Changes requested
- Approval workflow completed
- Approval workflow rejected
- Approval workflow cancelled
- Approval step skipped

An audit record may contain:

- Actor type
- Actor identifier
- Action
- Resource type
- Resource identifier
- Previous state
- New state
- Metadata
- Timestamp

Audit logging helps support accountability and investigation of workflow history.

---

# 20. Human-in-the-Loop Principle

Approval workflows represent a human authorization process.

The AI system may assist users by:

- Explaining approval requirements.
- Summarizing approval history.
- Identifying the current workflow stage.
- Explaining why a request is pending.
- Providing policy-related guidance.

However, the AI system should not independently approve or reject procurement requests.

Approval decisions remain controlled actions performed by authorized users.

For example, an AI assistant may say:

"The request requires Finance Manager approval before it can proceed."

However, it should not automatically approve the request on behalf of a Finance Manager.

---

# 21. AI and Live Approval Data

The AI system should distinguish between workflow knowledge and live workflow information.

Conceptual questions can use the knowledge base.

Examples:

- How does sequential approval work?
- What happens when an approver requests changes?
- Why are old approval steps skipped?

Questions about current approval data require an authorized transactional data source.

Examples:

- Who needs to approve my request?
- Is my purchase request approved?
- Which approval step is pending?
- Why is my request waiting?

Live approval information should be retrieved through controlled application services or tools rather than from the static RAG knowledge base.

---

# 22. Approval Workflow Summary

The approval process can be represented as:

Purchase Request Requires Approval

↓

Create Approval Workflow

↓

Create Approval Steps

↓

Validate Current Step

↓

Authorized Approver Decision

├── APPROVE
│
│   ↓
│
│ More Steps?
│
│ ├── Yes → Activate Next Step
│ │
│ └── No → Overall Approval APPROVED
│
├── REJECT
│
│   ↓
│
│ Overall Approval REJECTED
│
└── REQUEST CHANGES
    │
    ↓
    Overall Approval CHANGES_REQUESTED
    │
    ↓
    Purchase Request Updated
    │
    ↓
    Previous Approval CANCELLED
    │
    ↓
    Old Pending Steps SKIPPED
    │
    ↓
    Policy Re-evaluation
    │
    ↓
    New Approval Cycle, if Required

---

# 23. Key Principles

The ProcureOps approval workflow is based on the following principles:

- Authorization must be validated.
- Approval sequences must be respected.
- Only actionable steps may receive decisions.
- Previous approval cycles must not remain active after resubmission.
- Workflow operations should be transactionally consistent.
- Concurrent decisions should be controlled.
- Important workflow actions should be auditable.
- AI assistance should not bypass human authorization.

These principles help maintain a controlled, traceable, and reliable procurement approval process.