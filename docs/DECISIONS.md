# Architectural Decisions

This document records significant technical and design decisions made during development, along with the reasoning behind them.

# Design Decisions

This document records significant architectural and product decisions made during the development of the Accelerate Canvas Administration Suite.

The purpose of this document is to explain **why** decisions were made, not how they were implemented.

---

# August 2026

## Decision

Preview Before Apply

### Reason

Canvas administration changes can affect hundreds or thousands of objects.

Administrators should always have the opportunity to review proposed changes before they are written to Canvas.

### Outcome

Every management tool follows the same workflow:

Configure

↓

Preview

↓

Review

↓

Confirm

↓

Apply

↓

Results

---

## Decision

Shared Canvas API Layer

### Reason

Rather than allowing each workspace to communicate directly with Canvas, all API communication is centralized within the Canvas API service.

### Benefits

- Consistent API behavior
- Easier maintenance
- Shared authentication
- Centralized error handling

---

## Decision

Shared Course Authorization Service

### Reason

Customers often host Accelerate Education courses alongside courses from other vendors.

The hosted administration suite should operate only on eligible Accelerate Education courses.

### Outcome

A shared authorization service was introduced in:

tools/authorization.py

Every administration workspace uses the same verification process.

---

## Decision

Accelerate Course Verification

### Reason

Customers host courses differently and Accelerate does not control customer Canvas structures.

Reliable verification could not depend on:

- Course IDs
- Sub-Accounts
- Customer naming conventions

### Verification Rules

The application verifies eligibility using the course structure.

A course must:

- Contain "Resources" as its first module.
- Contain at least two of the required Accelerate resource markers within that module.

Verification details are intentionally hidden from customers.

Customer-facing messages simply indicate whether the selected course is eligible.

---

## Decision

Workspace Protection

### Reason

Customers should never accidentally preview or apply changes to an unauthorized course.

### Outcome

Management controls remain unavailable until the currently selected course has been successfully verified.

Changing the Course ID automatically clears previous verification results.

---

## Decision

Modular Workspace Design

### Reason

Each administration area should evolve independently.

### Outcome

Separate workspace files were created for:

- Quiz Management
- Assignment Management
- Course Management

A shared workspace controller is responsible only for routing.

---

## Decision

Reusable Tool Modules

### Reason

Business logic should remain independent of the user interface.

### Outcome

Canvas operations are implemented within the tools package while the UI focuses only on presentation and user interaction.

This separation simplifies testing, maintenance, and future expansion.