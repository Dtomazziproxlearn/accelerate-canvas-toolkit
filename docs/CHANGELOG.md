# Changelog

All notable changes to the Accelerate Canvas Administration Suite are documented in this file.

---

# Version 0.2 Alpha

**Status:** In Progress

## Added

- Redesigned the Course Management workspace.
- Introduced a numbered Course Management workflow.
- Added reusable UI rendering functions for improved maintainability.
- Replaced Course Management dropdowns with three-state action cards.
- Added Course Gating controls for:
  - Do Not Change
  - Enable
  - Disable
- Added Disable Course Gating support.
- Added read-only Preview support for removing:
  - Sequential module progression
  - Module prerequisites
  - Module-item completion requirements
- Added controlled execution for disabling Course Gating.
- Added detailed Course Gating execution results.
- Added Soft Zero Management to Course Management.
- Added support for enabling automatic grades for missing submissions.
- Added custom missing-submission grade values from 0% to 100%.
- Added support for disabling automatic missing-submission grades.
- Added Preview and Apply support for Soft Zero.
- Added shared Accelerate Education course verification.
- Added course verification before Course, Assignment, and Quiz Management controls are unlocked.
- Added automatic verification reset when the selected Course ID changes.
- Added generic customer-facing verification messages.
- Added an internal authorization service in `tools/authorization.py`.
- Added project documentation files and structure.
- Added the project README.
- Added project roadmap documentation.

## Improved

- Improved Course Management visual hierarchy.
- Improved Course Gating and Soft Zero control usability.
- Improved selected-state styling for configuration controls.
- Improved confirmation messaging for destructive Course Gating changes.
- Improved Preview summaries for Enable and Disable operations.
- Improved workspace state cleanup when the Course ID changes.
- Improved consistency across Configure, Preview, Apply, and Results workflows.

## Fixed

- Fixed Course Gating Disable execution so all prerequisites and completion requirements are removed.
- Fixed Soft Zero Disable handling.
- Fixed Course Management CSS so action-card styling no longer affects sidebar radio controls.
- Fixed stale verification state carrying over between Course IDs.
- Fixed stale Preview and execution data carrying over between course targets.

## In Progress

- Due Date Management
- Version 0.2 Alpha release documentation
- Reports workspace planning
- Sub-account authorization and processing design

---

# Version 0.1 Alpha

**Status:** Complete

## Initial Release

### Added

- Streamlit-based application shell.
- Administration Dashboard.
- Canvas connection sidebar.
- Canvas API connection testing.
- Single Course and Sub-Account target selection.
- Quiz & Exam Management workspace.
- Assignment Management workspace.
- Course Management workspace.
- Reports placeholder.
- Settings placeholder.
- Canvas API service layer.
- Preview-before-Apply workflow.
- Explicit confirmation before Canvas changes.
- Execution results and success/failure summaries.

### Quiz & Exam Management

- Added Classic Quiz retrieval.
- Added quiz and exam filtering.
- Added quiz attempt limit management.
- Added scoring-policy management.
- Added Shuffle Answers controls.
- Added One Question at a Time controls.
- Added exam password management.
- Added student quiz response controls.
- Added correct-answer visibility controls.
- Added Quiz & Exam Preview.
- Added Quiz & Exam Apply workflow.
- Added course-level execution results.
- Added sub-account-level quiz processing.

### Assignment Management

- Added assignment retrieval.
- Added filtering to exclude:
  - Classic Quizzes
  - Discussions
  - Non-online assignments
- Added assignment attempt-limit management.
- Added support for attempt limits from 1 to 10.
- Added Unlimited Attempts support.
- Added Assignment Preview.
- Added Assignment Apply workflow.
- Added execution summaries.
- Added confirmation before applying assignment changes.

### Course Management

- Added Course Gating Preview.
- Added Enable Course Gating support.
- Added sequential module progression.
- Added prerequisite chaining based on Canvas module order.
- Added completion requirements for supported module items:
  - Pages
  - Files
  - External URLs
  - External Tools
  - Assignments
  - Discussions
  - Quizzes
- Added Course Gating Apply workflow.
- Added detailed module and module-item execution results.

### Branding and Interface

- Added Accelerate Education branding.
- Added the Accelerate Education logo to the sidebar.
- Added the Accelerate Canvas Administration Suite header.
- Added branded navigation cards.
- Added branded sidebar styling.
- Added application footer and version display.