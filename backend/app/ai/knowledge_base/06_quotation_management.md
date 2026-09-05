# Quotation Management

## 1. Purpose

This document describes quotation management within the ProcureOps procurement application.

A quotation represents a vendor's commercial response to a Request for Quotation (RFQ). Quotations allow vendors to provide pricing and related information for goods or services requested through the procurement process.

Quotation management supports:

- Vendor quotation submission
- Quotation item management
- Vendor and RFQ validation
- Commercial price comparison
- Quotation analysis
- Procurement decision support

This document is intended for conceptual and procedural questions.

Current quotation information, including prices, vendor responses, and comparison results, should be retrieved from authorized live application data.

---

# 2. Quotation Overview

A quotation is submitted by a vendor in response to an RFQ.

A quotation is associated with:

- An RFQ
- A vendor
- One or more quotation items

The quotation represents the vendor's commercial offer for the requested goods or services.

The relationship can be represented as:

RFQ

↓

Invited Vendors

↓

Vendor Quotation

↓

Quotation Items

↓

Quotation Comparison

A single RFQ may receive quotations from multiple vendors.

---

# 3. Quotation Lifecycle

The quotation lifecycle is connected to the RFQ lifecycle.

A typical process is:

RFQ Created

↓

Vendors Added

↓

RFQ Issued

↓

Vendor Invited

↓

Vendor Submits Quotation

↓

RFQ Closed

↓

Quotations Compared

The application should validate that quotations are associated with valid procurement records.

---

# 4. Vendor and RFQ Relationship

A vendor should be associated with the relevant RFQ before submitting a quotation.

The system should prevent a vendor from submitting a quotation for an unrelated RFQ.

Before accepting a quotation, the application may validate:

- The RFQ exists.
- The vendor exists.
- The vendor is associated with the RFQ.
- The RFQ is in a valid state for quotation submission.
- The vendor is eligible to submit a quotation.

This maintains the integrity of the procurement process.

---

# 5. Quotation Information

A quotation may contain commercial information such as:

- Quotation identifier
- RFQ identifier
- Vendor identifier
- Quotation reference number
- Submission date
- Total amount
- Currency
- Additional remarks

The exact quotation model depends on the application's implementation.

The quotation record represents the overall commercial response.

Individual item-level pricing is represented separately through quotation items.

---

# 6. Quotation Items

A quotation may contain one or more quotation items.

Each quotation item represents pricing information for a requested procurement item.

A quotation item may contain:

- Quotation identifier
- RFQ item reference
- Unit price
- Quantity
- Total item amount
- Remarks

Example:

Item:

Laptop Computer

Quantity:

10

Unit Price:

90,000

Item Total:

900,000

Quotation items provide the detailed commercial information required for quotation analysis.

---

# 7. Price Calculation

The total amount for a quotation item may be calculated using:

Quantity × Unit Price

Example:

Quantity:

10

Unit Price:

90,000

Calculation:

10 × 90,000

Item Total:

900,000

The overall quotation amount may represent the total value of all applicable quotation items.

The exact calculation rules depend on the application's business logic.

---

# 8. Quotation Submission

Quotation submission represents the creation of a vendor's commercial response to an RFQ.

Before accepting a quotation, the application should validate the relevant relationships and workflow state.

A controlled quotation submission process may include:

1. Validate that the RFQ exists.
2. Validate that the vendor exists.
3. Validate that the vendor is associated with the RFQ.
4. Validate that the RFQ is in a valid state.
5. Validate quotation data.
6. Create the quotation.
7. Create quotation items.
8. Record the transaction.
9. Create an audit record when required.

If the quotation submission fails, related database changes should be rolled back.

---

# 9. Quotation Validation

Quotation information should be validated before it is stored.

Typical validation may include:

- Valid vendor identifier
- Valid RFQ identifier
- Vendor participation in the RFQ
- Valid item references
- Valid quantities
- Valid prices
- Required fields
- Numeric precision

Invalid quotation data should be rejected.

The application should not silently create incomplete or inconsistent commercial records.

---

# 10. Quotation and RFQ Status

The RFQ status controls the quotation process.

A quotation should generally be submitted while the RFQ is active.

Conceptually:

RFQ Status: ISSUED

↓

Quotation Submission Allowed

RFQ Status: CLOSED

↓

Quotation Submission Closed

The exact implementation rules should be enforced by the application service layer.

---

# 11. Quotation Comparison

Quotation comparison allows procurement users to evaluate commercial responses from multiple vendors.

A comparison is performed using quotations associated with the same RFQ.

Example:

RFQ-001

Vendor A

Total: 90,000

Vendor B

Total: 100,000

Vendor C

Total: 95,000

The comparison result may show:

- Vendor information
- Quotation information
- Item pricing
- Total amounts

The comparison process helps users identify differences between commercial offers.

---

# 12. RFQ Closure Before Comparison

Quotation comparison is intended to occur after the RFQ has been closed.

This creates a clear separation between:

Quotation Collection

and

Quotation Evaluation

Example:

RFQ ISSUED

↓

Quotations Submitted

↓

RFQ CLOSED

↓

Quotation Comparison

The application may reject comparison attempts when the RFQ is not CLOSED.

---

# 13. Comparison With Multiple Quotations

An RFQ may contain multiple quotations.

Example:

Vendor A

Quotation Total: 90,000

Vendor B

Quotation Total: 100,000

The comparison result allows users to identify differences between vendor responses.

A comparison may include one or more quotations.

The application should not assume that multiple quotations will always be available.

---

# 14. Comparison With One Quotation

An RFQ may contain only one quotation.

In this scenario, comparison can still return the available quotation.

Example:

RFQ Status:

CLOSED

Quotation Count:

1

Result:

The available quotation is returned.

The absence of competing quotations should not necessarily create an application error.

---

# 15. Comparison Without Quotations

An RFQ may be closed without receiving quotations.

In this situation:

RFQ Status:

CLOSED

Quotation Count:

0

The comparison operation may return an empty result.

Example:

No quotations available for comparison.

This represents a valid result rather than necessarily indicating a technical failure.

---

# 16. Commercial Comparison

Quotation comparison can support commercial analysis.

Typical information that may be compared includes:

- Total quotation amount
- Item-level prices
- Vendor responses
- Currency
- Quotation reference information

The comparison service should return actual application data.

The AI assistant may analyze the returned data, but it should not invent commercial values.

---

# 17. Lowest Price Analysis

A basic commercial comparison may identify the lowest quoted price.

Example:

Vendor A:

90,000

Vendor B:

100,000

Vendor C:

95,000

Lowest Amount:

90,000

Lowest Vendor:

Vendor A

However, the lowest price does not automatically mean that a vendor should be selected.

Other considerations may include:

- Product specifications
- Delivery capability
- Vendor reliability
- Commercial terms
- Business requirements

The final procurement decision should remain under human control.

---

# 18. AI-Assisted Quotation Analysis

The AI system can assist users in understanding quotation data.

For example, the AI may:

- Summarize quotations.
- Identify price differences.
- Identify the lowest quoted amount.
- Explain significant differences.
- Generate comparison summaries.

Example user question:

"Which vendor submitted the lowest quotation?"

The application should retrieve current quotation data through an authorized tool.

The AI can then analyze the returned data.

The process should be:

User Question

↓

Intent Classification

↓

Authorization Validation

↓

Retrieve Live Quotation Data

↓

AI Analysis

↓

Response

The AI should not generate quotation prices that are not present in the retrieved data.

---

# 19. Human-in-the-Loop

Quotation analysis may influence procurement decisions.

For this reason, AI-generated recommendations should remain advisory.

The AI may say:

"Vendor A submitted the lowest commercial quotation based on the available total amount."

However, the AI should not automatically:

- Select a vendor.
- Award a contract.
- Modify a quotation.
- Reject a quotation.
- Change procurement records.

Final decisions should remain with authorized users.

---

# 20. Quotation Data Integrity

The application should maintain valid relationships between:

- RFQs
- Vendors
- Quotations
- Quotation items

The system should prevent:

- Quotations for nonexistent RFQs.
- Quotations from unrelated vendors.
- Invalid item references.
- Invalid numeric values.
- Inconsistent commercial data.

Database constraints and service-layer validation help maintain integrity.

---

# 21. Transaction Integrity

Quotation operations may create multiple related records.

For example:

Quotation

↓

Quotation Items

↓

Audit Log

These changes should be treated as part of a logical transaction.

If an unexpected error occurs during processing, the transaction should be rolled back.

This prevents partial quotation records.

---

# 22. Audit Logging

Important quotation operations should be auditable.

Relevant events may include:

- Quotation created
- Quotation updated
- Quotation item added
- Quotation comparison performed, when audit requirements apply

An audit record may contain:

- Actor information
- Action
- Resource type
- Resource identifier
- Previous state
- New state
- Metadata
- Timestamp

Audit records provide traceability for important procurement activities.

---

# 23. Live Data and AI

The knowledge base explains how quotation management works.

However, the knowledge base does not contain current quotation data.

Questions such as:

- What quotations exist for RFQ-101?
- Which vendor quoted the lowest price?
- Show me quotation prices.
- Compare quotations for RFQ-101.

Require authorized access to live application data.

The AI system should retrieve the information through controlled application tools.

The static RAG knowledge base should be used for conceptual information.

---

# 24. AI Safety and Guardrails

The AI system should follow several important rules when handling quotation information.

The AI should:

- Use authorized tools for live quotation data.
- Clearly distinguish retrieved data from generated analysis.
- Avoid inventing prices.
- Avoid making unauthorized procurement changes.
- Treat recommendations as advisory.

The AI should not:

- Modify quotation records without authorization.
- Automatically select vendors.
- Invent missing quotations.
- Fabricate prices or totals.
- Bypass procurement workflow controls.

---

# 25. Quotation Management Summary

The quotation workflow can be represented as:

RFQ Created

↓

Vendors Added

↓

RFQ Issued

↓

Vendor Invitation

↓

Quotation Submitted

↓

Quotation Items Recorded

↓

RFQ Closed

↓

Quotation Comparison

↓

AI-Assisted Analysis

↓

Human Procurement Decision

---

# 26. Key Principles

The ProcureOps quotation management process is based on the following principles:

- Quotations must be associated with valid RFQs.
- Vendors should be associated with the relevant RFQ.
- Quotation data must be validated.
- Commercial information must remain accurate.
- Quotation comparison occurs after RFQ closure.
- Comparison may return zero, one, or multiple quotations.
- Live quotation data should be retrieved through authorized tools.
- AI analysis is advisory.
- AI should not invent commercial information.
- Procurement decisions remain under human control.
- Important actions should remain traceable and auditable.

These principles help ensure that quotation management remains reliable, controlled, and suitable for AI-assisted procurement analysis.