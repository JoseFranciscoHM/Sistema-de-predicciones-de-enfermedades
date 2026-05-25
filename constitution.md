# Project Constitution

> This document establishes the **non-negotiable principles** of the project.
> The AI agent **CANNOT** contradict these directives under any circumstance.
> This is the supreme authority within the SDD Harness.

---

## I. Development Principles (NON-NEGOTIABLE)

1. **Spec-First:**
   No implementation code shall be written before the specification (`spec.md`)
   and the implementation plan (`plan.md`) have been **approved by a human**.
   The agent MUST NOT generate production code during the `/specify` or `/plan`
   phases.

2. **Mandatory Testing (TDD):**
   All new code MUST be accompanied by tests (unit and/or integration) that:
   - **FAIL** without the new code (RED phase)
   - **PASS** with the new code (GREEN phase)
   The Harness enforces this cycle strictly. Skipping tests is a violation.

3. **Decision Log Immutability:**
   Every design decision that affects more than one file MUST be recorded in
   `memory/decision-log.md` with the date, context, and justification.
   This file is **append-only** for the agent — it MUST NOT modify or delete
   existing entries.

4. **Separation of Concerns:**
   - The **specification** (`spec.md`) describes **WHAT** the system does.
     It is technology-agnostic.
   - The **plan** (`plan.md`) describes **HOW** it will be implemented.
     It is technology-specific.
   These two documents serve different purposes and MUST NOT be conflated.

5. **Principle of Least Astonishment:**
   Generated code must be predictable and follow the conventions established in
   `rules/coding-standards.md`. Any deviation MUST be explicitly justified in
   the plan with a clear rationale.

---

## II. Language and Style Standards (NON-NEGOTIABLE)

6. **Code Language:**
   All source code (variable names, function names, class names, comments in
   code) MUST be written in **English**.

7. **Documentation Language:**
   Documentation files (specs, plans, READMEs, decision logs) MAY be written
   in **English or Spanish**, at the developer's discretion. Both languages are
   equally valid.

8. **Naming Convention:**
   - Variables and functions: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Classes and types: `PascalCase`
   - File names: `snake_case` (with appropriate extensions)

---

## III. Quality Standards (GATES)

9. **Quality Gate Compliance:**
   The agent MUST execute all applicable quality gates defined in
   `rules/quality-gates.json` before marking any task as completed.
   Failure to pass a mandatory gate BLOCKS the task from completion.

10. **Human Approval Gates:**
    The following transitions require **explicit human approval**:
    - Specification → Plan (`/specify` → `/plan`)
    - Plan → Implementation (`/plan` → `/implement`)
    - Implementation → Merge/Deploy (pre-merge gate)

---

## IV. Agent Behavioral Constraints

11. **No Autonomous Progression:**
    The agent MUST NOT advance to the next SDD phase without explicit human
    approval. Asking "shall I proceed?" and receiving no response does NOT
    constitute approval.

12. **Failure Escalation:**
    If the agent fails a quality gate or review **twice consecutively** on the
    same task, it MUST pause execution and request human guidance. It MUST NOT
    attempt a third fix autonomously.

13. **Scope Discipline:**
    The agent MUST NOT implement functionality that is not described in the
    approved specification. If it identifies missing functionality, it MUST
    flag it as a question and wait for human input before proceeding.
