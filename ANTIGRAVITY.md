# Instructions for Antigravity (Project Initialization)

> **This file activates the SDD Harness.** The agent MUST follow these
> instructions as its FIRST action before processing any other request.

---

## 1. Harness Initialization (MANDATORY FIRST ACTION)

Before processing any other instruction, you MUST execute the following steps
in order:

### 1.1. Locate the Harness

The SDD Harness is located at `.antigravity/harness/` relative to this file.
If the directory does not exist, clone it:

```bash
git clone https://github.com/Marianinpb/antigravity-sdd-harness.git .antigravity/harness
```

### 1.2. Load Configuration

Read and LOAD into your context the following files from `.antigravity/harness/`:

1. **`harness-config.yaml`** — Project configuration (tech stack, security profile)
2. **`constitution.md`** — Non-negotiable principles (supreme authority)
3. **`workflows/sdd-lifecycle.md`** — The main development lifecycle
4. **`rules/coding-standards.md`** — Coding conventions to enforce
5. **`rules/security-rules.md`** — Security rules for the active profile
6. **`rules/quality-gates.json`** — Quality gates to validate against

### 1.3. Load Project Context

Read the following files if they contain content:
1. **`memory/project-context.md`** — Current project state
2. **`memory/decision-log.md`** — Historical decisions

### 1.2.1. Detección de Tipo de Proyecto Especializado

Después de cargar `harness-config.yaml`, si `project.type` coincide con un tipo
definido en `workflows/registry.yaml` → `project_types`:

1. Cargar las plantillas especializadas desde `project_types/{tipo}/`.
2. Estas plantillas tienen **prioridad** sobre las genéricas en `templates/`.
3. Respetar las reglas específicas del tipo listadas en `registry.yaml` → `project_types.{tipo}.rules`.
4. Para el tipo `exposition`:
   - Los datos del expositor (título, autor, institución, fecha) **SIEMPRE** se
     preguntan explícitamente al usuario. **NUNCA** se infieren de la fuente.
   - El idioma por defecto es español. Cambio solo con confirmación humana explícita.
   - Los assets LaTeX solo se copian al ejecutar la tarea de generación de presentación.

---

## 2. Acknowledgment (MANDATORY)

Once the files are loaded, you MUST confirm to the user:

```
✅ SDD Harness activated.
- Project: [name from harness-config.yaml]
- Type: [type from harness-config.yaml]
- Specialized Template: [Yes — project_types/{tipo}/ | No]
- Security Profile: [profile from harness-config.yaml]
- Quality Gates: [enabled/disabled]

Ready to receive SDD commands:
  /specify  — Start Phase 1: Discovery and Specification
  /plan     — Start Phase 2: Design and Planning
  /implement — Start Phase 3: Implementation (TDD)
  /review   — Trigger quality gates and code review
```

---

## 3. Operational Mode

From this point forward, your **sole objective** is to follow the rules and
workflows defined in `.antigravity/harness/`.

- You MUST follow the SDD lifecycle phases in order.
- You MUST NOT skip phases or proceed without human approval.
- You MUST enforce all rules marked as `enforce: true` in `harness-config.yaml`.
- Any deviation from the harness rules is considered a **system error**.

---

## 4. Quick Reference

| Command | Phase | Description |
|---------|-------|-------------|
| `/specify` | 1 | Analyze requirements, ask questions, generate specification |
| `/plan` | 2 | Read approved spec, design architecture, create implementation plan |
| `/implement` | 3 | Execute tasks with TDD (RED → GREEN → REFACTOR) |
| `/review` | - | Run quality gates, self-review, validate compliance |
