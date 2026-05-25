# SDD Lifecycle: Specification-Driven Development

> This is the **master workflow document**. It defines the complete development
> lifecycle that the agent MUST follow in every iteration, from idea to
> working code.
>
> **Authority:** This workflow is subordinate only to `constitution.md`.

---

## Overview

```
┌─────────────┐     Approval     ┌─────────────┐     Approval     ┌──────────────┐
│   /specify  │ ───────────────► │    /plan     │ ───────────────► │  /implement  │
│   Phase 1   │                  │   Phase 2    │                  │   Phase 3    │
│  Discovery  │  ◄─── Reject ── │   Design     │  ◄─── Reject ── │     TDD      │
└─────────────┘                  └─────────────┘                  └──────┬───────┘
                                                                         │
                                                                         ▼
                                                                  ┌──────────────┐
                                                                  │   /review    │
                                                                  │ Quality Gates│
                                                                  └──────┬───────┘
                                                                         │
                                                              Pass ──────┼────── Fail
                                                                ▼        │        ▼
                                                           ✅ Done       │   🔄 Retry
                                                                         │   (max 2x)
                                                                         ▼
                                                                  🛑 Pause &
                                                                  Ask Human
```

---

## Soporte para Tipos de Proyecto Especializados

El harness soporta tipos de proyecto con plantillas y entregables adaptados que
se integran en el flujo SDD estándar **sin alterar las fases ni los comandos**.

Cuando `project.type` en `harness-config.yaml` coincide con un tipo definido en
`workflows/registry.yaml` → `project_types`, el agente DEBE:

1. **Usar las plantillas del tipo de proyecto** en lugar de las genéricas de
   `templates/`. Las plantillas especializadas tienen prioridad absoluta.
2. **Generar los entregables específicos** del tipo (definidos en `outputs`).
3. **Copiar assets adicionales** solo cuando la tarea correspondiente lo indique
   (`copy_condition`). No copiar al inicio del proyecto.
4. **Respetar las reglas del tipo** definidas en `project_types.{tipo}.rules`.

### Tipos de proyecto con soporte especializado

| Tipo | Descripción | Plantillas |
|------|-------------|------------|
| `exposition` | Presentaciones académicas | `project_types/exposition/` |

> **REGLAS CRÍTICAS para `exposition`:**
>
> 1. Los datos del expositor (título, autor, institución, fecha) **SIEMPRE** se
>    preguntan explícitamente al usuario durante `/specify`. **NUNCA** se infieren
>    del contenido de la fuente (paper, libro, repositorio).
>    El autor de la fuente ≠ el expositor.
>
> 2. El idioma de los entregables es **español por defecto**. Solo se cambia con
>    confirmación humana explícita. El idioma de la fuente NO determina el idioma
>    de la presentación.
>
> 3. Los assets LaTeX solo se copian al directorio `presentacion/` del proyecto
>    cuando el tipo es `exposition` y se ejecuta la tarea de generación de presentación.

---

## Phase 1: Discovery and Specification (`/specify`)


**Goal:** Transform a natural language description into a formal, unambiguous
specification document.

**Trigger:** User invokes `/specify` with a feature description.

### Steps

1. **RECEIVE:** The agent receives a description of the new functionality
   in natural language from the human.

2. **ANALYZE CONTEXT:** The agent reads:
   - `memory/project-context.md` — to understand the current project state
   - `memory/decision-log.md` — to understand past decisions and avoid conflicts
   - `harness-config.yaml` — to understand the tech stack and constraints

3. **IDENTIFY AMBIGUITIES:** The agent analyzes the description and identifies:
   - Ambiguous requirements
   - Missing information
   - Implicit assumptions
   - Edge cases not addressed
   
   The agent formulates **clear, specific questions** and presents them to the
   human. It **MUST NOT** make assumptions about ambiguous requirements.

4. **GENERATE SPECIFICATION:** Once ambiguities are resolved, the agent
   generates a specification file using `templates/spec-template.md`:
   - Location: `specs/{SPEC-ID}-{name}.md`
   - Uses RFC-2119 keywords (MUST, SHOULD, MAY)
   - Includes all functional and non-functional requirements
   - Includes acceptance criteria (testable)

5. **PRESENT FOR APPROVAL:** The agent presents the specification to the human
   and waits for explicit approval.
   
   > **GATE:** The agent **CANNOT** proceed to Phase 2 without explicit human
   > approval of the specification.

### Exit Criteria
- [ ] Specification file created at `specs/{SPEC-ID}-{name}.md`
- [ ] All questions answered by human
- [ ] Human has explicitly approved the specification

---

## Phase 2: Design and Planning (`/plan`)

**Goal:** Convert an approved specification into a detailed technical
implementation plan.

**Trigger:** User invokes `/plan` (specification must be approved).

### Steps

1. **READ SPECIFICATION:** The agent reads the approved specification
   (`specs/{SPEC-ID}-{name}.md`).

2. **DESIGN ARCHITECTURE:** The agent creates a detailed implementation plan
   using `templates/plan-template.md`:
   - Component architecture and relationships
   - File structure (new, modified, deleted files)
   - Dependencies (internal and external)
   - Data models (using `templates/data-model-template.md` if needed)
   
3. **DECOMPOSE INTO TASKS:** The agent breaks the plan into atomic tasks
   using `templates/tasks-template.md`:
   - Each task MUST include `_Boundary_` annotation (scope limitation)
   - Each task MUST include `_Depends_` annotation (prerequisite tasks)
   - Tasks are ordered by dependency graph
   - Each task has defined acceptance criteria and test requirements

4. **CHECK AGAINST RULES:** The agent validates the plan against:
   - `rules/coding-standards.md` — naming, conventions
   - `rules/security-rules.md` — security profile requirements
   - `constitution.md` — non-negotiable principles

5. **PRESENT FOR APPROVAL:** The agent presents the plan and task breakdown
   to the human and waits for explicit approval.
   
   > **GATE:** The agent **CANNOT** proceed to Phase 3 without explicit human
   > approval of the plan.

### Exit Criteria
- [ ] Plan file created at `plans/{PLAN-ID}-{name}.md`
- [ ] Task breakdown created at `tasks/{PLAN-ID}-tasks.md`
- [ ] All tasks have `_Boundary_` and `_Depends_` annotations
- [ ] Human has explicitly approved the plan

---

## Phase 3: Implementation (`/implement`)

**Goal:** Execute the approved plan task by task using Test-Driven Development.

**Trigger:** User invokes `/implement` (plan must be approved).

### Steps (Per Task)

1. **SELECT TASK:** The agent selects the highest-priority task from the task
   breakdown that:
   - Is not yet completed (`[ ]` status)
   - Has all dependencies resolved (all `_Depends_` tasks are `[x]`)

2. **WRITE TEST (RED):** The agent writes a unit test and/or integration test
   for the functionality described in the task.
   - The test MUST target the acceptance criteria defined in the task
   - The agent runs the test and **verifies it FAILS**
   - If the test passes without implementation, the test is insufficient

3. **IMPLEMENT (GREEN):** The agent writes the **minimum amount of code**
   necessary to make the test pass.
   - Code MUST follow `rules/coding-standards.md`
   - Code MUST respect `rules/security-rules.md`
   - Code MUST NOT exceed the task's `_Boundary_`

4. **REFACTOR (OPTIONAL):** The agent refactors the code if needed:
   - Tests MUST still pass after refactoring
   - Refactoring MUST NOT change behavior
   - Refactoring SHOULD improve readability, reduce duplication, or improve
     performance

5. **REVIEW (`/review`):** The agent triggers the review phase for this task.
   (See Phase: Review below.)

6. **PROPAGATE LESSONS:** Lessons learned during implementation are recorded:
   - In `## Implementation Notes` section of the plan
   - In `memory/decision-log.md` if a design decision was made

7. **UPDATE TASK STATUS:** Mark the task as completed (`[x]`) in the task
   breakdown and update the progress summary.

8. **REPEAT:** If more tasks remain, return to Step 1.

### Exit Criteria
- [ ] All tasks in the breakdown are marked `[x]`
- [ ] All tests pass
- [ ] All quality gates pass
- [ ] Implementation notes are documented

---

## Phase: Review (`/review`)

**Goal:** Validate the implementation against all quality gates and rules.

**Trigger:** Automatically after each task in `/implement`, or manually
by the user.

### Steps

1. **EXECUTE QUALITY GATES:** The agent runs all applicable quality gates
   from `rules/quality-gates.json`:
   - Only gates matching the project's `tech_stack` are executed
   - Mandatory gates MUST pass; optional gates produce warnings

2. **SELF-REVIEW:** The agent performs a self-review checking:
   - Compliance with `rules/coding-standards.md`
   - Compliance with `rules/security-rules.md`
   - Compliance with `constitution.md`
   - Code stays within the task's `_Boundary_`

3. **HANDLE RESULTS:**
   - ✅ **All checks pass:** Task is marked as completed.
   - ❌ **Check fails (1st time):** Agent fixes the issue and re-runs checks.
   - ❌ **Check fails (2nd time):** Agent fixes and re-runs one more time.
   - 🛑 **Check fails (3rd time):** Agent MUST pause and request human guidance.
     It MUST NOT attempt a third autonomous fix.

4. **RECORD DECISION:** If any non-trivial decision was made during the review
   (e.g., trade-off between coverage and complexity), it MUST be logged in
   `memory/decision-log.md`.

### Exit Criteria
- [ ] All mandatory quality gates pass
- [ ] Self-review confirms compliance with all rules
- [ ] Any decisions logged in decision-log.md

---

## Lifecycle Rules

1. **No Phase Skipping:** Phases MUST be executed in order. The agent CANNOT
   jump from `/specify` to `/implement` without going through `/plan`.

2. **Human Approval Gates:** Phase transitions require explicit human approval.
   Silence or non-response does NOT constitute approval.

3. **Iteration:** If the human rejects a specification or plan, the agent
   returns to the beginning of that phase with the feedback incorporated.

4. **Scope Creep Protection:** During `/implement`, if the agent identifies
   functionality not covered by the specification, it MUST flag it and wait
   for human input. It MUST NOT implement unspecified features.

5. **Documentation Trail:** Every artifact (spec, plan, tasks, decision log)
   is a living document. The agent appends to them but MUST NOT delete
   previous content.
