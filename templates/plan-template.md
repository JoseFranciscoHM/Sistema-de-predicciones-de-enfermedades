# Implementation Plan: [PLAN-ID] [Feature Name]

> **Status:** Draft | Under Review | Approved
> **Specification:** [Link to approved spec: specs/XX-name.md]
> **Author:** [Name]
> **Date:** [YYYY-MM-DD]
> **Approved by:** [Name] on [YYYY-MM-DD]

---

## 1. Overview

_Brief summary of how this feature will be implemented. Reference the approved
specification and explain the technical approach chosen._

**Approach:**
[Describe the technical strategy in 2-3 sentences.]

**Key Design Decisions:**
- [Decision 1 and rationale]
- [Decision 2 and rationale]

---

## 2. Architecture

_Describe the high-level architecture of the implementation. How do the
components fit together?_

### 2.1. Component Diagram

```
[Diagram: component relationships, data flow, interfaces]
```

### 2.2. Technology Choices

| Component | Technology | Justification |
|-----------|-----------|---------------|
| [Component 1] | [Tech] | [Why this choice] |
| [Component 2] | [Tech] | [Why this choice] |

---

## 3. File Structure

_List all files that will be created, modified, or deleted._

### New Files
| File Path | Purpose |
|-----------|---------|
| `[path/to/file]` | [What this file does] |

### Modified Files
| File Path | Changes |
|-----------|---------|
| `[path/to/file]` | [What changes] |

### Deleted Files
| File Path | Reason |
|-----------|--------|
| `[path/to/file]` | [Why it's being removed] |

---

## 4. Dependencies

_List all external dependencies required for this implementation._

| Dependency | Version | Purpose | New? |
|-----------|---------|---------|------|
| [Dep 1] | [Version] | [Why needed] | Yes/No |

---

## 5. Task Breakdown

_Each task MUST include `_Boundary_` and `_Depends_` annotations._

### Task 1: [Task Title]
- **ID:** TASK-01
- **_Boundary_:** [Exactly what files/functions this task touches — nothing more]
- **_Depends_:** [None | TASK-XX, TASK-YY]
- **Description:** [What needs to be done]
- **Tests:** [What tests will be written for this task]
- **Estimated complexity:** Low | Medium | High

### Task 2: [Task Title]
- **ID:** TASK-02
- **_Boundary_:** [Scope limitation]
- **_Depends_:** [TASK-01]
- **Description:** [What needs to be done]
- **Tests:** [What tests will be written for this task]
- **Estimated complexity:** Low | Medium | High

---

## 6. Data Models

_Reference or inline the data model definitions. Use `data-model-template.md`
for complex models._

| Entity | Fields | Relationships |
|--------|--------|---------------|
| [Entity 1] | [Key fields] | [Related entities] |

---

## 7. Error Handling Strategy

_How will errors be handled across the implementation?_

| Error Scenario | Handling Strategy | User Impact |
|---------------|-------------------|-------------|
| [Scenario 1] | [How it's handled] | [What user sees] |

---

## 8. Implementation Notes

_This section is filled DURING the `/implement` phase. Lessons learned,
deviations from the plan, and notes for future tasks go here._

> **Note:** This section is append-only during implementation. Do not delete
> existing notes.

### [Date] — [Task ID]
- [Note about what was learned or changed]

---

## 9. Verification Plan

_How will we verify that this implementation meets the specification?_

### Automated Tests
- [ ] [Test description and command]

### Manual Verification
- [ ] [Manual verification step]

---

## 10. Rollback Plan

_If the implementation fails or causes issues, how do we revert?_

- [Step 1: How to undo changes]
- [Step 2: How to restore previous state]
