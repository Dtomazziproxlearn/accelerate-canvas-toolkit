# Roadmap

This document outlines the planned direction of the Accelerate Canvas Administration Suite.

The roadmap is a living document and will evolve as new capabilities are identified and development priorities change.

---

# Version 0.2 Alpha
## Course Management

### Status

🟡 In Progress

### Completed

### Completed

- Course Gating Controls
- Soft Zero Management
- Preview Changes
- Apply Changes

### Remaining Work

#### Due Date Management

Manage assignment and assessment due dates across an entire course.

Planned capabilities:

- Shift all due dates forward or backward
- Preserve relative assignment spacing
- Preview all proposed changes
- Apply changes
- Execution summary

---

# Version 0.3 Alpha
## Sub-Account Management

### Goal

Expand all supported administration tools from single-course scope to Canvas sub-account scope.

### Planned Capabilities

- Discover courses within a selected sub-account
- Include or exclude child sub-accounts
- Filter by:
  - Enrollment term
  - Course status
  - Course name
  - Course ID
- Preview affected courses before execution
- Execute Quiz, Assignment and Course Management tools across multiple courses

---

## Background Job Processing

### Goal

Support long-running operations without requiring the browser session to remain active.

Example:

- 100 Courses
- 50 Quizzes per Course
- 5,000 Quiz Updates

### Planned Capabilities

- Background processing queue
- Unique Job IDs
- Live progress tracking
- Percentage complete
- Current course being processed
- Success / Failure counts
- Retry temporary API failures
- Respect Canvas API rate limits
- Prevent duplicate submissions
- Safe cancellation
- Completion summaries

### Job Statuses

- Queued
- Preparing
- Running
- Completed
- Completed with Errors
- Failed
- Cancelled

---

# Version 0.4 Alpha
## Reports & Job History

### Goal

Provide administrators with complete visibility into previous operations performed by the application.

### Job History

Each job should record:

- Job ID
- Tool executed
- User
- Canvas Instance
- Scope
- Selected settings
- Start time
- Completion time
- Duration
- Final status
- Success count
- Failure count
- Skipped count

### Job Details

Allow administrators to review:

- Courses processed
- Items processed
- Requested changes
- Successful updates
- Skipped items
- Failed items
- Error messages
- Retry history

### Reporting

- Search
- Filtering
- CSV Export
- Error Reports
- Retry Failed Items
- Re-run Previous Job
- Historical retention

---

# Future Enhancements

These features are currently under consideration and are not assigned to a specific release.

## Blueprint Management

- Blueprint synchronization tools
- Blueprint lock management
- Blueprint reporting

---

## User Management

- Bulk user management
- Enrollment management
- Role updates
- User reporting

---

## Security & Governance

- Confirmation workflow for destructive operations
- Impact summaries
- Typed confirmation for large jobs
- Role-based permissions
- Audit logging
- Secure handling of Canvas API tokens

---

## Reliability

- Resume interrupted jobs
- Intelligent retry logic
- Duplicate operation detection
- Configurable concurrency
- API rate-limit management

---

## Notifications

- In-app completion notifications
- Optional email notifications

#### Late Submission Deductions

Deferred for a future Course Management development phase.

This capability will eventually support automatic deductions for
late submissions, including deduction percentages, intervals, and
minimum-grade limits.