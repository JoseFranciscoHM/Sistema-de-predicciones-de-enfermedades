# Command: /specify

> **Phase:** 1 — Discovery and Specification
> **Purpose:** Transform a natural language feature description into a formal,
> unambiguous specification document.

---

## Trigger

The user invokes this command with a description of the desired functionality.
Examples:
- `/specify I need a temperature sensor driver that reads from ADC channel 3`
- `/specify Create a data pipeline that processes CSV files and generates plots`
- `/specify Add UART communication between two ESP32 modules`

---

## Pre-Conditions

1. The harness MUST be activated (ANTIGRAVITY.md loaded).
2. `harness-config.yaml` MUST have `project.name` and `project.type` defined.
3. `memory/project-context.md` SHOULD be populated (empty is acceptable for
   new projects).

---

## Execution Steps

### Step 1: Acknowledge and Parse

The agent acknowledges the request and parses the natural language description
to extract:
- **What** the feature does (functional intent)
- **Who** uses or interacts with it (actors)
- **Where** it fits in the existing system (integration points)
- **Why** it's needed (problem being solved)

### Step 2: Load Context

The agent reads:
- `memory/project-context.md` — current project state
- `memory/decision-log.md` — past decisions that may affect this feature
- Any existing specifications in `specs/` — to avoid contradictions

### Step 3: Identify Ambiguities

The agent analyzes the description for:
- **Vague terms** ("fast", "efficient", "good") → ask for quantifiable criteria
- **Missing boundaries** (input ranges, output formats, error conditions)
- **Implicit assumptions** (hardware availability, network access, dependencies)
- **Edge cases** (empty inputs, maximum loads, concurrent access)
- **Conflicting requirements** (with existing specs or decisions)

The agent presents a numbered list of questions to the human:

```
📋 Questions before I can write the specification:

1. [Question about ambiguous requirement]
2. [Question about missing boundary condition]
3. [Question about assumed hardware/software]
```

> **RULE:** The agent MUST NOT proceed with generating the specification until
> all critical ambiguities are resolved. It MAY proceed with minor ambiguities
> noted as assumptions in the spec.

### Step 4: Generate Specification

Using `templates/spec-template.md`, the agent creates:
- **File location:** `specs/{SPEC-ID}-{descriptive_name}.md`
- **SPEC-ID format:** `SPEC-XX` where XX is a zero-padded sequential number
- **Content:** All sections of the template filled with the analyzed requirements

> **Project Type Override:** If `project.type` in `harness-config.yaml` matches
> a type defined in `registry.yaml` → `project_types`, the agent MUST use the
> `templates_override.spec` template instead of `templates/spec-template.md`.
>
> **Para el tipo `exposition` específicamente:**
> 1. El agente DEBE solicitar EXPLÍCITAMENTE al usuario todos los datos del
>    expositor (título, autor, institución, fecha, audiencia, duración) ANTES
>    de generar la especificación. Estos valores NUNCA deben inferirse de la fuente.
> 2. El agente lee la configuración de la fuente desde `harness-config.yaml` →
>    `exposition` para determinar el tipo de contenido (paper, tema+libro, repo).
> 3. El idioma de los entregables es español por defecto (`language: es`). El
>    agente NO DEBE cambiarlo sin confirmación humana explícita, aunque la fuente
>    esté en otro idioma.
> 4. Usar la plantilla: `project_types/exposition/spec_template.md`

Key rules for the specification:
- Use RFC-2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
- Every functional requirement MUST have a corresponding acceptance criterion
- Acceptance criteria MUST be testable (Given/When/Then format)
- Non-functional requirements MUST include quantifiable metrics where possible

### Step 5: Present for Approval

The agent presents the generated specification to the human with:

```
📄 Specification ready for review: specs/SPEC-XX-name.md

Summary:
- [Number] functional requirements
- [Number] non-functional requirements
- [Number] acceptance criteria
- [Number] open questions remaining

Please review and:
  ✅ Approve — to proceed to /plan
  ❌ Reject — with feedback for revision
  ✏️ Request changes — specific sections to modify
```

---

## Post-Conditions

- [ ] Specification file exists at `specs/{SPEC-ID}-{name}.md`
- [ ] All critical questions have been answered
- [ ] The specification has been approved by the human
- [ ] The agent is ready to proceed to `/plan`

---

## Error Handling

| Scenario | Action |
|----------|--------|
| User provides no description | Ask for a description before proceeding |
| `harness-config.yaml` is not configured | Prompt user to configure it first |
| Contradicts existing specification | Flag the contradiction and ask for resolution |
| User rejects specification | Incorporate feedback and regenerate from Step 4 |
