# Development Guide

This document contains development workflows, coding standards, project setup instructions, and best practices.

# Development Guide

This document provides guidance for setting up, running, and contributing to the Accelerate Canvas Administration Suite.

The goal is to ensure a consistent development experience and maintain a high standard of code quality throughout the project.

---

# Development Environment

## Technology Stack

- Python 3.9
- Streamlit
- Canvas LMS REST API
- Visual Studio Code

---

## Local Development

The application is designed to run locally using a Python virtual environment.

### Activate the virtual environment

macOS / Linux

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

---

### Install project dependencies

```bash
pip install -r requirements.txt
```

---

### Run the application

```bash
streamlit run app.py
```

The application will launch in your default web browser.

---

# Project Structure

```
Accelerate-Canvas-Toolkit/

assets/
docs/
reports/
tools/
ui/

app.py
canvas.py
config.py
engine.py
requirements.txt
README.md
```

---

## Folder Responsibilities

### assets/

Application images and branding resources.

---

### docs/

Project documentation.

Contains:

- Architecture
- Changelog
- Decisions
- Development Guide
- Releases
- Roadmap

---

### reports/

Generated reports and exported files.

---

### tools/

Contains Canvas business logic.

Current modules include:

- assignments.py
- authorization.py
- courses.py
- quizzes.py

Business logic should remain independent from the user interface.

---

### ui/

Contains all Streamlit user interface components.

Examples include:

- Dashboard
- Sidebar
- Workspace Controller
- Course Management
- Quiz Management
- Assignment Management

---

# Development Principles

The project follows several core principles.

## Separation of Responsibilities

The UI should only manage:

- User interaction
- Display
- Session State

Canvas operations should be implemented within the tools package.

---

## Centralized Canvas API

Canvas communication should occur only through:

```
canvas.py
```

New API requests should be added to the Canvas service rather than being implemented directly within workspaces.

---

## Shared Components

Whenever possible, functionality should be shared across management tools.

Examples include:

- Course Verification
- Preview generation
- Confirmation workflow
- Execution summaries

Avoid duplicating logic between workspaces.

---

# User Experience Standards

Every management tool should follow the same workflow.

```
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
```

Consistency is preferred over introducing unique workflows for individual tools.

---

# Documentation Standards

All significant development work should be reflected in the project documentation.

Typical updates include:

CHANGELOG.md

Feature additions

Bug fixes

Improvements

---

ROADMAP.md

Future development plans

---

DECISIONS.md

Architectural and product decisions

---

RELEASES.md

Major release summaries

---

README.md

Project overview and current capabilities

---

# Code Standards

Functions should be:

- Small
- Focused
- Well documented

Comments should explain intent rather than obvious implementation details.

Use descriptive variable and function names.

Favor readability over clever implementations.

---

# Testing Expectations

New functionality should be tested within a Canvas test environment before being considered complete.

Whenever practical, testing should include:

- Preview generation
- Apply Changes
- Success scenarios
- Failure scenarios
- Edge cases
- Verification of changes directly within Canvas

---

# Release Process

Typical development workflow:

1. Implement the feature.
2. Perform local testing.
3. Test against a Canvas test course.
4. Fix discovered issues.
5. Update project documentation.
6. Record release notes.
7. Create a project backup.
8. Begin the next development milestone.

---

# Versioning

Development currently follows an Alpha release model.

Example:

Version 0.1 Alpha

↓

Version 0.2 Alpha

↓

Version 0.3 Alpha

Future stable releases will follow semantic versioning as the project matures.

---

# Future Development

Planned future work includes:

- Sub-Account Management
- Background Job Processing
- Reports and Job History
- Blueprint Management
- User Management
- Developer Tools
- Notifications
- Additional Canvas administration capabilities

# Development Guide

This document provides guidance for setting up, running, and contributing to the Accelerate Canvas Administration Suite.

The goal is to ensure a consistent development experience and maintain a high standard of code quality throughout the project.

---

# Technology Stack

The Accelerate Canvas Administration Suite is built using the following technologies:

- Python 3.9
- Streamlit
- Canvas LMS REST API
- Visual Studio Code

---

# Setting Up the Project

This section explains how to configure the project on a new development computer.

## Prerequisites

Install the following software before beginning:

- Python 3.9
- Visual Studio Code
- Git (optional but recommended)

---

## Step 1 — Obtain the Project

Copy or clone the project folder.

Example:

```
Accelerate-Canvas-Toolkit/
```

The project should contain folders similar to:

```
Accelerate-Canvas-Toolkit/

assets/
docs/
reports/
tools/
ui/

app.py
canvas.py
config.py
engine.py
requirements.txt
README.md
```

Do **not** copy the following folders from another developer's machine:

```
.venv/
__pycache__/
```

These folders are machine-specific and should always be recreated locally.

---

## Step 2 — Open the Project

Open Visual Studio Code.

Select:

```
File
↓
Open Folder...
↓
Accelerate-Canvas-Toolkit
```

---

## Step 3 — Open a Terminal

In Visual Studio Code:

```
Terminal
↓
New Terminal
```

Verify that the terminal is inside the project folder.

macOS / Linux

```bash
pwd
```

Example output:

```
/Users/username/Desktop/Accelerate-Canvas-Toolkit
```

---

## Step 4 — Create a Virtual Environment

Create a new Python virtual environment.

```bash
python3 -m venv .venv
```

This creates an isolated Python environment for the project.

---

## Step 5 — Activate the Virtual Environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

The command prompt should now display:

```
(.venv)
```

at the beginning of the line.

---

## Step 6 — Install Project Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

This installs Streamlit and all additional project dependencies.

---

## Step 7 — Verify the Environment

Confirm that Python is coming from the virtual environment.

```bash
which python
```

Expected:

```
.../Accelerate-Canvas-Toolkit/.venv/bin/python
```

Confirm that pip is also using the virtual environment.

```bash
which pip
```

Expected:

```
.../Accelerate-Canvas-Toolkit/.venv/bin/pip
```

---

## Step 8 — Run the Application

Start the application.

```bash
streamlit run app.py
```

The terminal should display something similar to:

```
Local URL:

http://localhost:8501
```

Open the URL in a browser if it does not launch automatically.

---

## Step 9 — Connect to Canvas

Within the application:

Enter:

- Canvas URL
- Canvas API Token

Click:

**Test Connection**

Once connected, the application is ready for use.

---

# Updating the Project

When receiving project updates from another developer:

1. Activate the virtual environment.

```bash
source .venv/bin/activate
```

2. Install any new dependencies.

```bash
pip install -r requirements.txt
```

3. Start the application.

```bash
streamlit run app.py
```

---

# Project Structure

```
Accelerate-Canvas-Toolkit/

assets/
docs/
reports/
tools/
ui/

app.py
canvas.py
config.py
engine.py
requirements.txt
README.md
```

---

# Folder Responsibilities

## assets/

Contains project branding, logos, icons and images.

---

## docs/

Contains all project documentation.

Current documentation includes:

- ARCHITECTURE.md
- CHANGELOG.md
- DECISIONS.md
- DEVELOPMENT.md
- RELEASES.md
- ROADMAP.md

---

## reports/

Stores generated reports and exported files.

---

## tools/

Contains Canvas business logic.

Current modules include:

- assignments.py
- authorization.py
- courses.py
- quizzes.py

Business logic should remain independent from the user interface.

---

## ui/

Contains all Streamlit user interface components.

Examples include:

- Dashboard
- Sidebar
- Workspace Controller
- Course Management
- Quiz Management
- Assignment Management

---

# Development Principles

The application follows several core principles.

## Separation of Responsibilities

The UI is responsible for:

- User interaction
- Display
- Session State

Canvas business logic belongs inside the **tools** package.

---

## Centralized Canvas API

Canvas communication should occur only through:

```
canvas.py
```

New API requests should always be added to the Canvas service rather than being implemented directly inside workspaces.

---

## Shared Components

Whenever practical, functionality should be shared across management tools.

Examples include:

- Course Verification
- Preview generation
- Confirmation workflow
- Execution summaries

Avoid duplicating business logic.

---

# User Experience Standards

Every management tool should follow the same workflow.

```
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
```

Consistency should always take priority over introducing different workflows for individual tools.

---

# Documentation Standards

Significant development work should always be reflected in the project documentation.

Typical updates include:

### CHANGELOG.md

- Feature additions
- Improvements
- Bug fixes

---

### ROADMAP.md

- Future development plans

---

### DECISIONS.md

- Architectural decisions
- Product decisions

---

### RELEASES.md

- Major software milestones

---

### README.md

- Project overview
- Current capabilities

---

# Coding Standards

Functions should be:

- Small
- Focused
- Well documented

Prefer descriptive function names and variable names.

Comments should explain intent rather than obvious implementation details.

Favor readability over clever implementations.

---

# Testing Expectations

All new functionality should be tested within a Canvas test environment before being considered complete.

Testing should include:

- Preview generation
- Apply Changes
- Successful operations
- Failure scenarios
- Edge cases
- Verification of Canvas changes

---

# Common Issues

## "python: command not found"

Use:

```bash
python3
```

or verify that the virtual environment has been activated.

---

## "No module named streamlit"

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## "which python" returns nothing

The virtual environment is not active.

Activate it:

```bash
source .venv/bin/activate
```

---

## Project Folder Was Renamed

If the project folder is renamed after the virtual environment was created, the virtual environment may contain invalid paths.

The recommended solution is:

```bash
rm -rf .venv
```

Create a new virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Best Practices

- Never commit the `.venv` folder.
- Never commit `__pycache__`.
- Always activate the virtual environment before development.
- Install packages using `requirements.txt`.
- Test changes in a Canvas test environment.
- Update project documentation whenever significant features are added.

---

# Release Process

Typical development workflow:

1. Implement the feature.
2. Perform local testing.
3. Test against a Canvas test course.
4. Fix discovered issues.
5. Update project documentation.
6. Update release notes.
7. Create a project backup.
8. Begin the next development milestone.

---

# Versioning

The project currently follows an Alpha release model.

Example:

Version 0.1 Alpha

↓

Version 0.2 Alpha

↓

Version 0.3 Alpha

As the platform matures, versioning may transition to semantic versioning.

---

# Future Development

Planned future work includes:

- Sub-Account Management
- Background Job Processing
- Reports and Job History
- Blueprint Management
- User Management
- Developer Tools
- Notifications
- Additional Canvas administration capabilities