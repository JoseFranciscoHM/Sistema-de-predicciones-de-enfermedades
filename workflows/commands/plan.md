# Command: /plan

> **Phase:** 2 — Design and Planning
> **Purpose:** Convert an approved specification into a detailed technical
> implementation plan with atomic task breakdown.

---

## Trigger

The user invokes `/plan` after a specification has been approved.
The agent MAY also suggest transitioning to `/plan` after approval.

---

## Pre-Conditions

1. A specification (`specs/{SPEC-ID}-{name}.md`) MUST be approved.
2. The harness MUST be activated.
3. `harness-config.yaml` MUST define the technology stack.

---

## Execution Steps

### Step 1: Read Approved Specification

The agent reads the approved specification and extracts:
- All functional requirements (MUST, SHOULD, MAY)
- All non-functional requirements
- All acceptance criteria
- All constraints and assumptions
- Actor interactions

### Step 2: Design Architecture

The agent designs the technical solution:

1. **Component identification:** What modules/components are needed?
2. **Interface design:** How do components communicate?
3. **Data model:** What data structures are needed? (Use
   `templates/data-model-template.md` for complex models)
4. **Technology mapping:** Which technologies from the `tech_stack` apply
   to each component?
5. **File structure:** What files will be created, modified, or deleted?

> **Project Type Override:** If `project.type` in `harness-config.yaml` matches
> a type defined in `registry.yaml` → `project_types`, the agent MUST use the
> `templates_override.plan` and `templates_override.tasks` templates instead of
> the generic ones in `templates/`.
>
> **Para el tipo `exposition`:** El plan y el desglose de tareas son en gran
> medida predefinidos en las plantillas especializadas. El agente los adapta al
> tipo de fuente específico (paper, tema+libro, repo) pero sigue la estructura
> de fases predefinida:
> - Fase A: Recolección de datos del expositor (SIEMPRE primera)
> - Fase B: Análisis de la fuente y generación de resumen
> - Fase C: Generación de la presentación LaTeX (con copia condicional de assets)
> - Fase D: Generación del guion de exposición
>
> Usar las plantillas:
> - Plan: `project_types/exposition/plan_template.md`
> - Tareas: `project_types/exposition/tasks_template.md`

### Step 3: Identify Dependencies

The agent lists:
- **External dependencies:** New packages, libraries, or tools needed
- **Internal dependencies:** Existing code that this feature depends on
- **Environmental dependencies:** Hardware, services, configurations

### Step 4: Decompose into Tasks

Using `templates/tasks-template.md`, the agent creates atomic tasks:

Each task MUST include:
```markdown
### Task N: [Title]
- **ID:** TASK-XX
- **_Boundary_:** [Exactly what this task touches — files, functions, modules]
- **_Depends_:** [None | TASK-XX, TASK-YY]
- **Description:** [What to implement]
- **Tests:** [What tests to write — aligned with acceptance criteria]
- **Complexity:** Low | Medium | High
```

**Task decomposition rules:**
- A task SHOULD be completable in a single implementation cycle
- A task MUST NOT modify files outside its `_Boundary_`
- Dependencies MUST form a DAG (no circular dependencies)
- The first task in each dependency chain MUST have `_Depends_: None`

### Step 5: Validate Against Rules

The agent checks the plan against:
- `rules/coding-standards.md` — naming conventions respected?
- `rules/security-rules.md` — security profile requirements addressed?
- `rules/quality-gates.json` — are tests planned for each task?
- `constitution.md` — does the plan follow all non-negotiable principles?

### Step 6: Present for Approval

```
📋 Implementation plan ready for review:
- Plan: plans/PLAN-XX-name.md
- Tasks: tasks/PLAN-XX-tasks.md

Summary:
- [N] tasks across [M] phases
- [N] new files, [M] modified files
- [N] external dependencies
- Estimated complexity: [Low/Medium/High]

Please review and:
  ✅ Approve — to proceed to /implement
  ❌ Reject — with feedback for revision
  ✏️ Request changes — specific sections to modify
```

---

## Post-Conditions

- [ ] Plan file exists at `plans/{PLAN-ID}-{name}.md`
- [ ] Task breakdown exists at `tasks/{PLAN-ID}-tasks.md`
- [ ] All tasks have `_Boundary_` and `_Depends_` annotations
- [ ] Plan validated against rules and constitution
- [ ] Human has explicitly approved the plan

---

## Error Handling

| Scenario | Action |
|----------|--------|
| No approved specification exists | Direct user to run `/specify` first |
| Tech stack not defined | Prompt user to complete `harness-config.yaml` |
| Circular dependencies detected | Restructure task decomposition |
| User rejects plan | Incorporate feedback and redesign from Step 2 |
| Specification contradicts existing code | Flag issue, log in decision-log, ask human |
