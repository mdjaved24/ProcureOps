# ProcureOps Procurement Knowledge Base

## 1. Purpose

This knowledge base provides domain information about procurement concepts and the workflows supported by the ProcureOps application.

It is intended to support retrieval-augmented generation (RAG), AI assistants, and intelligent procurement workflows. The content focuses on explaining procurement concepts, processes, terminology, and relationships between major procurement entities.

This knowledge base should be used for answering general and procedural procurement questions. Real-time information such as the current status of a purchase request, active vendors, RFQs, approvals, or quotations should be retrieved from the application's transactional database rather than relying on this knowledge base.

---

# 2. What Is Procurement?

Procurement is the business process of acquiring goods, services, or works from external suppliers or vendors.

Procurement involves more than simply purchasing an item. A complete procurement process may include:

1. Identifying a business requirement.
2. Creating a purchase request.
3. Reviewing and approving the request.
4. Identifying potential vendors.
5. Requesting quotations.
6. Receiving vendor quotations.
7. Comparing available quotations.
8. Selecting an appropriate vendor.
9. Completing the procurement process.

The purpose of procurement is to ensure that organizational requirements are fulfilled efficiently, economically, and according to applicable business policies.

A procurement system typically provides controls around authorization, approval, vendor selection, documentation, and auditability.

---

# 3. Procurement and Purchasing

Procurement and purchasing are related concepts but are not identical.

Purchasing generally refers to the activity of buying goods or services.

Procurement is a broader process that may include:

- Requirement identification
- Budget or policy validation
- Purchase request creation
- Approval workflows
- Vendor management
- RFQ management
- Quotation collection
- Quotation comparison
- Supplier selection
- Purchasing activities

Therefore, purchasing can be considered one component of the larger procurement lifecycle.

---

# 4. Procurement Lifecycle

A simplified procurement lifecycle is:

Requirement Identification
↓
Purchase Request Creation
↓
Review and Approval
↓
Vendor Identification
↓
RFQ Creation
↓
RFQ Issuance
↓
Quotation Submission
↓
Quotation Comparison
↓
Vendor Selection
↓
Procurement Completion

The exact lifecycle can vary depending on organizational policies, purchase value, risk level, and approval requirements.

---

# 5. Purchase Requests

A purchase request represents an internal request to procure goods or services.

A purchase request generally contains information such as:

- Request number
- Request title
- Description
- Requested items
- Quantity
- Estimated amount
- Currency
- Requesting user
- Current workflow status

The purchase request acts as the starting point for a controlled procurement workflow.

Creating a purchase request does not necessarily mean that the organization has approved the purchase. The request may need to pass through review and approval processes before procurement activities continue.

---

# 6. Purchase Request Workflow

A purchase request may move through multiple workflow states.

Typical states include:

## DRAFT

The purchase request is being prepared and has not yet entered the formal workflow.

The requester may modify the purchase request while it remains in the draft state.

---

## SUBMITTED

The purchase request has been submitted for processing.

At this stage, the request may proceed to review, policy evaluation, or approval depending on the application's workflow.

---

## UNDER_REVIEW

The purchase request is being reviewed as part of the procurement workflow.

The request may proceed toward approval or may be rejected depending on the applicable process.

---

## APPROVAL_PENDING

The purchase request requires one or more approval decisions.

The request remains pending until the required approval workflow is completed.

---

## APPROVED

The required approval workflow has been successfully completed.

Approval indicates that the request is authorized to proceed to subsequent procurement activities according to the application's business process.

---

## CHANGES_REQUESTED

An approver or reviewer has requested changes to the purchase request.

The requester may update the relevant information and resubmit the request.

When a request is resubmitted, the approval workflow may need to be evaluated again based on the updated request information and applicable policies.

---

## REJECTED

The purchase request has been rejected.

A rejected request cannot automatically continue through the normal approval workflow.

---

## CANCELLED

The purchase request has been cancelled.

Cancelled requests are treated as inactive and cannot continue through normal processing.

---

## COMPLETED

The purchase request has completed its applicable procurement workflow.

Completion indicates the end of the workflow supported by the application.

---

# 7. Purchase Request Resubmission

Resubmission is used when a purchase request has received a request for changes.

A typical resubmission process includes:

1. The purchase request enters the CHANGES_REQUESTED state.
2. The requester updates the necessary information.
3. Previous active approval cycles are closed.
4. Pending steps from the previous approval cycle are no longer actionable.
5. The purchase request is evaluated against the applicable policy again.
6. A new approval workflow may be created if required.
7. The purchase request proceeds according to the new workflow outcome.

Closing the previous approval cycle is important because approval decisions from an earlier version of a request should not remain active after significant changes have been made.

This approach preserves historical information while preventing obsolete approval steps from being acted upon.

---

# 8. Approval Workflows

An approval workflow is a controlled sequence of decisions required before a purchase request can proceed.

An approval workflow may contain:

- Approval record
- Approval status
- Multiple approval steps
- Required roles
- Approval sequence
- Decision information
- Decision timestamps
- Decision comments

An approval workflow can require multiple users or organizational roles to participate.

---

# 9. Sequential Approval

In a sequential approval workflow, approval steps must be completed in a defined order.

For example:

Sequence 1
↓
Procurement Manager
↓
Sequence 2
↓
Finance Manager
↓
Sequence 3
↓
Senior Approver

The second approval step should not become actionable until the first step has been approved.

Similarly, later steps should remain unavailable while earlier steps are still pending.

Sequential workflows provide clear control over authorization and reduce the risk of bypassing required approvals.

---

# 10. Approval Decisions

An authorized approver may make one of several decisions.

Typical decisions include:

## Approve

The approval step is accepted.

The workflow may proceed to the next approval step.

If all required steps are approved, the overall approval may be marked as approved and the associated purchase request may proceed to the APPROVED state.

---

## Reject

The approval step is rejected.

The overall approval workflow may be marked as rejected.

The associated purchase request may also transition to the REJECTED state.

---

## Request Changes

The approver requires modifications before the request can continue.

The approval workflow may move to a CHANGES_REQUESTED state.

The associated purchase request may also move to CHANGES_REQUESTED.

The requester can then update and resubmit the request according to the application's workflow.

---

# 11. Procurement Policies

Procurement policies define rules that control procurement workflows.

Policies may determine whether a purchase request:

- Requires approval
- Requires specific approval roles
- Requires additional workflow steps
- Can proceed without approval
- Requires different treatment based on request characteristics

Policy decisions may be based on attributes such as:

- Estimated purchase amount
- Currency
- Request type
- Organizational rules
- Risk conditions

For example, a policy may specify that purchase requests above a certain value require management approval.

Policies provide consistency and reduce the need to manually determine approval requirements for every purchase request.

---

# 12. Vendors

A vendor, also known as a supplier, is an external organization or entity that provides goods or services.

Vendor information may include:

- Vendor code
- Vendor name
- Description
- Email address
- Phone number
- Address
- City
- State
- Country
- Postal code
- Tax identification information
- Vendor status

Vendor records provide a structured representation of suppliers participating in the procurement process.

Vendor information should be maintained consistently to support reliable RFQ and quotation workflows.

---

# 13. Vendor Status

A vendor may have an operational status that determines whether the vendor should be actively used in procurement workflows.

For example, an organization may maintain active and inactive vendors.

Vendor status helps prevent inappropriate use of vendors that are no longer operational or approved for participation in procurement activities.

Changes to vendor status should be auditable.

---

# 14. Request for Quotation (RFQ)

An RFQ, or Request for Quotation, is a formal request sent to one or more vendors asking them to provide pricing and commercial information for specified goods or services.

An RFQ may include:

- RFQ number
- Title
- Description
- Requested items
- Quantities
- Units
- Submission deadline
- Invited vendors
- Issue date
- RFQ status

The purpose of an RFQ is to collect comparable vendor quotations.

---

# 15. RFQ Lifecycle

An RFQ may move through the following lifecycle.

## DRAFT

The RFQ is being prepared.

The organization may add items, update RFQ information, and select vendors.

The RFQ has not yet been formally issued to vendors.

---

## ISSUED

The RFQ has been formally issued.

Invited vendors can participate in the quotation process according to the application's workflow.

An RFQ should generally have appropriate vendor participation before it is issued.

---

## CLOSED

The quotation submission process has ended.

Once an RFQ is closed, the organization can evaluate the quotations received.

Closing an RFQ provides a clear boundary between quotation submission and quotation evaluation.

---

## CANCELLED

The RFQ has been cancelled.

Cancelled RFQs should not continue through the normal quotation workflow.

---

# 16. RFQ Vendor Invitations

An RFQ may be associated with multiple vendors.

Each vendor association represents an invitation or participation relationship between the vendor and the RFQ.

An RFQ vendor record may contain:

- RFQ identifier
- Vendor identifier
- Invitation status
- Invitation timestamp

A vendor invitation can be used to track which vendors were included in an RFQ process.

---

# 17. Quotations

A quotation is a vendor's commercial response to an RFQ.

A quotation may contain information such as:

- RFQ reference
- Vendor reference
- Quoted amount
- Currency
- Quotation items
- Submission information
- Commercial details

Quotations allow the organization to evaluate vendor responses to the same procurement requirement.

---

# 18. Quotation Comparison

Quotation comparison is the process of evaluating multiple vendor responses.

Comparison may include:

- Total quoted amount
- Item-level pricing
- Vendor identity
- Currency
- Submission status
- Differences between vendor prices

A lower price may be an important factor, but the lowest quotation is not always automatically the best business decision.

Organizations may also consider:

- Vendor reliability
- Product quality
- Delivery capability
- Commercial terms
- Compliance requirements
- Organizational policy

The ProcureOps quotation comparison functionality is intended to provide structured information that supports decision-making.

---

# 19. Transactional Data and Knowledge Base Data

The ProcureOps AI system distinguishes between two types of information.

## Knowledge Base Information

Knowledge base information includes relatively stable explanatory content such as:

- Procurement concepts
- Workflow explanations
- Process definitions
- Policy explanations
- RFQ concepts
- Quotation evaluation concepts

This information is suitable for retrieval-augmented generation.

---

## Transactional Information

Transactional information includes dynamic application data such as:

- Current purchase request status
- Specific purchase request details
- Current approval status
- Pending approvals
- Active vendors
- Current RFQs
- Submitted quotations
- Latest quotation prices

This information should be retrieved from the application's database or through controlled tools.

It should not be treated as static knowledge base content because it can change over time.

---

# 20. AI Retrieval Principles

When answering a procurement-related question, the AI system should first determine what type of information is required.

If the user asks a conceptual question, such as:

"What is an RFQ?"

the system should retrieve relevant information from the procurement knowledge base.

If the user asks a live-data question, such as:

"What is the status of purchase request PR-001?"

the system should use an authorized application tool or database query.

For questions that require both conceptual and transactional information, the AI system may combine:

1. Knowledge retrieval.
2. Application tool calls.
3. Structured reasoning.
4. A final generated response.

The AI system should avoid presenting retrieved information as real-time transactional data unless that information was obtained from an authorized live data source.

---

# 21. Auditability

Procurement systems require traceability.

Important actions may be recorded in an audit log, including:

- Purchase request status changes
- Approval decisions
- Approval status changes
- Purchase request resubmission
- Vendor creation
- Vendor updates
- Vendor status changes
- RFQ issuance
- RFQ closure
- RFQ cancellation

Audit records can capture information such as:

- Actor
- Actor type
- Action
- Resource type
- Resource identifier
- Previous state
- New state
- Timestamp
- Additional metadata

Auditability supports troubleshooting, accountability, and workflow traceability.

---

# 22. Important AI Safety Principle

The AI assistant should provide information and assistance but should not bypass business controls.

The AI system should not independently:

- Approve a purchase request
- Reject an approval
- Modify procurement data without authorization
- Change vendor status without permission
- Cancel procurement records without authorization

Actions that modify transactional data should be performed through controlled application services and authorization checks.

For sensitive or high-impact actions, the system should support human confirmation before execution.

---

# 23. Summary

ProcureOps manages a structured procurement workflow involving:

Purchase Requests
↓
Approval Workflows
↓
Vendors
↓
RFQs
↓
Quotations
↓
Quotation Comparison

The AI system complements this workflow by providing intelligent assistance.

The retrieval-augmented generation system is intended to answer questions about procurement concepts and workflow knowledge.

Dynamic application information should be obtained from authorized tools or database services.

This separation between static knowledge and live transactional data helps create a more reliable, secure, and production-oriented AI architecture.