# Request for Quotation (RFQ) Workflow

## 1. Purpose

This document describes the Request for Quotation (RFQ) workflow supported by the ProcureOps procurement application.

An RFQ is used to request commercial quotations from one or more vendors for goods or services associated with a procurement requirement.

The RFQ workflow provides a controlled process for:

- Creating an RFQ
- Associating procurement items
- Adding vendors
- Issuing the RFQ
- Tracking vendor invitations
- Closing the RFQ
- Cancelling the RFQ
- Supporting quotation comparison

This document provides conceptual and procedural information.

Questions about the current status or details of a specific RFQ should be answered using authorized live transactional data rather than relying on the static knowledge base.

---

# 2. RFQ Overview

An RFQ, or Request for Quotation, is a formal request sent to vendors asking them to provide pricing and related commercial information for specific goods or services.

An RFQ may contain:

- RFQ number
- Related purchase request
- Title
- Description
- Requested items
- Item quantities
- Units
- Submission deadline
- Invited vendors
- Issue date
- Current status
- Creator information
- Creation timestamp
- Update timestamp

The purpose of an RFQ is to collect vendor responses that can be compared as part of the procurement decision-making process.

---

# 3. Relationship Between Purchase Requests and RFQs

An RFQ is associated with a purchase request.

The purchase request represents the internal procurement requirement, while the RFQ represents the request sent to vendors for commercial quotations.

The relationship can be represented as:

Purchase Request

↓

RFQ

↓

RFQ Items

↓

Vendors Invited

↓

Vendor Quotations

↓

Quotation Comparison

The RFQ items are derived from or associated with the procurement requirement represented by the purchase request.

This relationship helps maintain traceability between the original business requirement and vendor quotations.

---

# 4. RFQ Lifecycle

The ProcureOps RFQ lifecycle contains the following primary states:

- DRAFT
- ISSUED
- CLOSED
- CANCELLED

The allowed transitions are:

DRAFT

↓

ISSUED

↓

CLOSED

An RFQ may also be cancelled.

The lifecycle can be represented as:

DRAFT
├── ISSUED
│      ├── CLOSED
│      └── CANCELLED
│
└── CANCELLED

CLOSED and CANCELLED are terminal states.

Once an RFQ reaches one of these states, it cannot return to a previous active state through the normal lifecycle.

---

# 5. RFQ Creation

An RFQ is created from a procurement requirement represented by a purchase request.

During creation, the system may store:

- Purchase request reference
- RFQ title
- Description
- Submission deadline
- Creator identity

The application generates or assigns a unique RFQ number.

A newly created RFQ begins in the DRAFT state.

Example:

RFQ Number:

RFQ-2026-001

Status:

DRAFT

The RFQ is not yet considered issued to vendors at this stage.

---

# 6. RFQ Number

The RFQ number uniquely identifies an RFQ within the procurement system.

The RFQ number may be used in:

- Procurement workflows
- Vendor communication
- Quotation records
- Audit records
- Reporting
- AI-assisted queries

RFQ numbers should be unique and consistently formatted.

The exact numbering strategy may depend on application requirements.

---

# 7. RFQ Draft State

The DRAFT state represents an RFQ that is still being prepared.

While an RFQ is in the DRAFT state, authorized users may perform activities such as:

- Updating the RFQ title
- Updating the description
- Updating the submission deadline
- Reviewing RFQ items
- Adding vendors

The RFQ should not be treated as formally issued while it remains in the DRAFT state.

Vendors should not be considered officially invited until the RFQ is issued.

---

# 8. RFQ Items

An RFQ contains one or more items for which vendor quotations are requested.

An RFQ item may contain:

- RFQ identifier
- Purchase request item reference
- Item name
- Description
- Quantity
- Unit

Example:

Item:

Laptop Computer

Quantity:

20

Unit:

PCS

RFQ items provide the basis for vendor quotations.

The item information should be sufficiently clear to allow vendors to provide relevant and comparable commercial responses.

---

# 9. Adding Vendors to an RFQ

An RFQ may be associated with multiple vendors.

Adding vendors occurs while the RFQ is in an appropriate state, typically DRAFT.

Before adding a vendor, the application should validate:

- The RFQ exists.
- The vendor exists.
- The vendor is eligible to participate.
- The RFQ allows vendor modifications.
- The vendor is not already associated with the RFQ.

Each vendor is represented by an RFQ vendor association.

This relationship allows the system to track participation independently for each vendor.

---

# 10. RFQ Vendor Association

An RFQ vendor association represents the relationship between:

- An RFQ
- A Vendor

The association may contain:

- RFQ identifier
- Vendor identifier
- Vendor participation status
- Invitation timestamp

Example:

RFQ-2026-001

↓

Vendor A

Status: INVITED

↓

Vendor B

Status: INVITED

This structure allows one RFQ to involve multiple vendors.

---

# 11. RFQ Issuance

Issuing an RFQ represents the transition from preparation to the active quotation collection stage.

Before an RFQ can be issued, the application should validate that the RFQ is eligible for issuance.

Typical validations may include:

- The RFQ exists.
- The RFQ is currently in the DRAFT state.
- The RFQ contains required item information.
- At least one vendor is associated with the RFQ.
- The submission deadline is valid.

If these conditions are satisfied, the RFQ may transition to ISSUED.

---

# 12. Issue Date

When an RFQ is issued, the application records the issue date.

The issue date represents the point at which the RFQ officially enters the active vendor quotation stage.

Example:

Status before issuance:

DRAFT

↓

RFQ Issued

↓

Status:

ISSUED

Issue Date:

2026-08-30

The issue date provides traceability and can be used when reviewing the RFQ lifecycle.

---

# 13. Vendor Invitation Status

When an RFQ is issued, associated vendors may be marked as INVITED.

The invitation status indicates that the vendor is included in the RFQ process.

Example:

Before RFQ issuance:

Vendor Status:

PENDING

After RFQ issuance:

Vendor Status:

INVITED

The invitation status allows the application to distinguish vendors that are associated with an RFQ from vendors that have been formally invited.

---

# 14. RFQ Issuance Validation

An RFQ should not be issued if important requirements are missing.

Examples of invalid issuance scenarios include:

- The RFQ does not exist.
- The RFQ is not in the DRAFT state.
- No vendors are associated with the RFQ.
- Required RFQ items are missing.
- The submission deadline is invalid.

Attempting to issue an RFQ that is already ISSUED should also be rejected.

Example:

Current Status:

ISSUED

Requested Action:

ISSUE

Result:

Invalid transition.

---

# 15. RFQ Submission Deadline

An RFQ may contain a submission deadline.

The deadline defines the expected end of the quotation submission period.

Example:

Issue Date:

2026-08-30

Submission Deadline:

2026-09-05

The deadline provides vendors with a defined period for preparing and submitting quotations.

The application may enforce additional rules regarding quotation submission based on the deadline.

---

# 16. Active RFQ State

An RFQ in the ISSUED state represents an active quotation request.

During this stage:

- Vendors are considered invited.
- Vendor quotations may be submitted according to application rules.
- The RFQ remains open until it is closed or cancelled.

The system should prevent invalid changes that could compromise the quotation process.

For example, modifications to fundamental RFQ information after issuance may require additional controls.

---

# 17. Closing an RFQ

Closing an RFQ ends the active quotation collection stage.

An RFQ may be closed when it is in the ISSUED state.

Example:

ISSUED

↓

CLOSE RFQ

↓

CLOSED

Once closed, the RFQ should no longer accept normal quotation submissions.

The CLOSED state creates a clear boundary between quotation collection and quotation evaluation.

---

# 18. RFQ Closure Validation

Before closing an RFQ, the application should validate:

- The RFQ exists.
- The RFQ is currently ISSUED.
- The requested transition is valid.

A DRAFT RFQ should not be closed directly.

Example:

Current Status:

DRAFT

Requested Action:

CLOSE

Result:

Invalid transition.

An RFQ that is already CLOSED should not be closed again.

---

# 19. RFQ Cancellation

Cancellation terminates the RFQ before or during the quotation process.

An RFQ may be cancelled when the lifecycle permits cancellation.

ProcureOps supports cancellation from:

- DRAFT
- ISSUED

Examples:

DRAFT

↓

CANCEL

↓

CANCELLED

or:

ISSUED

↓

CANCEL

↓

CANCELLED

---

# 20. RFQ Cancellation Validation

An RFQ should not be cancelled when it has already reached a terminal state.

Examples include:

Current Status:

CLOSED

Requested Action:

CANCEL

Result:

Invalid transition.

Similarly, an RFQ already in the CANCELLED state should not be cancelled again.

The application should validate lifecycle transitions before changing RFQ status.

---

# 21. Terminal States

CLOSED and CANCELLED are terminal RFQ states.

A terminal state represents the end of the normal RFQ lifecycle.

Once an RFQ is CLOSED or CANCELLED:

- It should not be issued again.
- It should not be returned to DRAFT.
- It should not be cancelled again through the normal workflow.
- Invalid lifecycle transitions should be rejected.

This prevents historical procurement records from being unintentionally reopened.

---

# 22. RFQ State Transition Rules

The allowed transitions can be represented as:

DRAFT

→ ISSUED

→ CANCELLED

ISSUED

→ CLOSED

→ CANCELLED

CLOSED

→ No further normal transitions

CANCELLED

→ No further normal transitions

The application should enforce these transitions at the service layer.

---

# 23. RFQs and Quotations

A quotation represents a vendor response to an RFQ.

The quotation process typically follows:

RFQ Created

↓

Vendors Added

↓

RFQ Issued

↓

Vendor Quotations Submitted

↓

RFQ Closed

↓

Quotation Comparison

The quotation should be associated with:

- The relevant RFQ
- The submitting vendor

This relationship ensures that vendor responses remain connected to the correct procurement requirement.

---

# 24. RFQ Closure and Quotation Comparison

Quotation comparison is performed after the RFQ has been closed.

This ensures that quotation evaluation occurs after the active submission stage has ended.

Example:

RFQ

Status: ISSUED

↓

Vendor Quotations Submitted

↓

RFQ CLOSED

↓

Quotation Comparison Available

The application may reject quotation comparison attempts when the RFQ has not yet reached the CLOSED state.

---

# 25. RFQ Without Quotations

An RFQ may be closed even when no quotations have been received, depending on the application's workflow.

Quotation comparison in this scenario may return an empty result.

Example:

RFQ Status:

CLOSED

Quotations:

0

Comparison Result:

No quotations available.

The absence of quotations should not necessarily cause an application error if the RFQ lifecycle itself is valid.

---

# 26. RFQ Audit Logging

Important RFQ actions should be recorded in the audit log.

Relevant audit events include:

- RFQ created
- RFQ updated
- Vendor added to RFQ
- RFQ issued
- RFQ closed
- RFQ cancelled

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

Example RFQ audit action:

RFQ_ISSUED

Audit logging provides traceability for procurement operations.

---

# 27. Transaction Integrity

RFQ lifecycle operations may update multiple records.

For example, issuing an RFQ may:

1. Update the RFQ status.
2. Set the issue date.
3. Update vendor invitation statuses.
4. Create an audit log.

These operations should be processed transactionally.

If an unexpected failure occurs, the transaction should be rolled back.

This prevents partial workflow updates.

Example of an invalid partial state:

RFQ Status:

ISSUED

Vendor Invitations:

Not Updated

Audit Log:

Missing

Transactional processing helps ensure that related changes are committed together.

---

# 28. Concurrency Control

RFQ lifecycle operations may be triggered simultaneously by multiple users.

Example:

User A attempts to issue an RFQ.

At the same time:

User B also attempts to issue the same RFQ.

Without concurrency control, both operations could potentially process the same state transition.

Critical RFQ operations may use database locking.

A controlled lifecycle operation may:

1. Lock the RFQ record.
2. Retrieve the current status.
3. Validate the requested transition.
4. Apply the transition.
5. Update related records.
6. Create an audit log.
7. Commit the transaction.

This helps prevent conflicting or duplicate lifecycle operations.

---

# 29. AI Usage Guidelines

The AI assistant may use this knowledge base to answer conceptual questions such as:

- What is an RFQ?
- How does the RFQ lifecycle work?
- Why can't a closed RFQ be cancelled?
- What happens when an RFQ is issued?
- Why are vendors marked as invited?
- When can quotation comparison occur?

These questions are suitable for RAG retrieval.

Questions requiring current transactional information should use authorized application tools.

Examples include:

- What is the status of RFQ-101?
- Which vendors were invited to RFQ-101?
- When is the submission deadline for RFQ-101?
- How many quotations were submitted?
- Is RFQ-101 currently open?

The AI system should retrieve this information from live transactional data rather than relying on the static knowledge base.

---

# 30. AI Safety and Human Control

The AI assistant may explain RFQ workflows and assist users with understanding the procurement process.

However, the AI should not independently:

- Issue an RFQ
- Close an RFQ
- Cancel an RFQ
- Add vendors to an RFQ
- Modify procurement data

These are controlled application actions.

If AI-assisted actions are implemented in the future, they should follow:

User Request

↓

Authorization Validation

↓

AI Action Proposal

↓

Human Confirmation

↓

Application Service Execution

↓

Audit Logging

This design ensures that AI assistance does not bypass existing business controls.

---

# 31. RFQ Workflow Summary

The complete RFQ workflow can be represented as:

Purchase Request

↓

Create RFQ

↓

RFQ Status: DRAFT

↓

Add RFQ Items

↓

Add Vendors

↓

Validate RFQ

↓

Issue RFQ

↓

RFQ Status: ISSUED

↓

Vendors Marked as INVITED

↓

Quotation Submission Period

↓

Close RFQ

↓

RFQ Status: CLOSED

↓

Quotation Comparison

An alternative termination path is:

DRAFT or ISSUED

↓

Cancel RFQ

↓

RFQ Status: CANCELLED

---

# 32. Key Principles

The ProcureOps RFQ workflow is based on the following principles:

- RFQs follow controlled lifecycle transitions.
- RFQs should contain the required procurement information.
- Vendors must be associated before RFQ issuance.
- Vendors are marked as invited when an RFQ is issued.
- CLOSED and CANCELLED RFQs are terminal states.
- Quotation comparison occurs after RFQ closure.
- Important lifecycle actions are auditable.
- Critical operations should maintain transaction integrity.
- Concurrent state transitions should be controlled.
- AI assistance should not bypass procurement authorization or lifecycle controls.

These principles help ensure that the RFQ process remains controlled, traceable, and suitable for reliable procurement operations.