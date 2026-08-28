# Architecture

This document describes the overall architecture and design of the application.

# Architecture

This document describes the overall architecture of the Accelerate Canvas Administration Suite.

The goal is to explain how the application is organized and how its major components interact.

---

# High-Level Architecture

The application is a browser-based administration platform built with Streamlit.

Customer Browser
        │
        ▼
Streamlit Application
        │
        ▼
Workspace Controller
        │
        ▼
Management Workspace
        │
        ▼
Business Logic (tools)
        │
        ▼
Canvas API Service
        │
        ▼
Canvas LMS

---

# Core Components

## app.py

Application entry point.

Responsibilities

- Initializes the Streamlit application.
- Loads the sidebar.
- Routes to the dashboard or active workspace.

---

## ui/

Contains all user interface components.

Current workspaces include:

- Dashboard
- Quiz Management
- Assignment Management
- Course Management
- Reports
- Settings

The UI is responsible only for presentation and user interaction.

Canvas business logic is intentionally excluded from this layer.

---

## workspace.py

Acts as the central workspace controller.

Responsibilities

- Routes users to the selected workspace.
- Manages shared Course Verification.
- Controls access to protected management tools.
- Resets verification when Course IDs change.

---

## tools/

Contains all Canvas business logic.

Current modules include:

- quizzes.py
- assignments.py
- courses.py
- authorization.py

Business logic is isolated from the user interface to improve maintainability and testing.

---

## canvas.py

Central Canvas API service.

Responsibilities

- Authentication
- GET requests
- POST requests
- PUT requests
- PATCH requests
- Canvas error handling

All Canvas communication is performed through this service.

---

## Session State

Streamlit Session State is used to manage application state.

Examples include:

- Connection status
- Selected target
- Preview data
- Confirmation state
- Execution results
- Course verification

Changing the selected Course ID automatically resets any state tied to the previous course.

---

# Current Workflow

All management tools follow the same workflow.

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

Execution Results

This provides a consistent user experience across the application.

---

# Course Authorization

Course Verification is shared across all supported management workspaces.

Verification is performed before administration controls become available.

Verification logic resides exclusively within:

tools/authorization.py

Customer-facing messages intentionally do not reveal internal verification criteria.

---

# Design Principles

The application follows several guiding principles.

- Separation of UI and business logic.
- Centralized Canvas API communication.
- Shared authorization across workspaces.
- Preview before Apply.
- Consistent execution summaries.
- Modular architecture.
- Reusable components.
- Readability over cleverness.
- Comprehensive inline documentation.

---

# Future Architecture

The application is designed to expand into a full Canvas administration platform.

Planned architectural additions include:

- Background job processing
- Sub-account processing
- Historical reporting
- Job queue
- Notifications
- Blueprint Management
- User Management