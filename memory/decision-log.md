# Decision Log

> **Rules:**
> - This file is **append-only**. The agent MUST NOT modify or delete existing entries.
> - Every design decision that affects more than one file MUST be recorded here.
> - Entries are ordered chronologically (newest at the bottom).

---

## Entry Format

```
### [DECISION-ID] — [Short Title]
- **Date:** YYYY-MM-DD
- **Context:** [What situation led to this decision]
- **Decision:** [What was decided]
- **Justification:** [Why this option was chosen over alternatives]
- **Alternatives Considered:** [What other options were evaluated]
- **Files Affected:** [List of files impacted by this decision]
- **Related:** [SPEC-ID, TASK-ID, or other references]
```

---

## Decisions

### DECISION-001 — Arquitectura del módulo de tipo de proyecto "exposition"
- **Date:** 2026-05-23
- **Context:** Se necesita extender el harness SDD Antigravity para soportar la
  generación automática de presentaciones académicas (exposiciones) a partir de
  papers PDF, temas con libro de referencia, o repositorios. El harness hasta
  ahora no distinguía entre tipos de proyecto especializados.
- **Decision:** Crear una carpeta `project_types/exposition/` con plantillas
  especializadas (spec, plan, tasks) y assets LaTeX parametrizados con placeholders.
  La selección del tipo se hace mediante `project.type: "exposition"` en
  `harness-config.yaml`. Los comandos existentes (`/specify`, `/plan`, `/implement`)
  detectan el tipo y usan las plantillas correspondientes automáticamente.
- **Justification:**
  1. Reutiliza al máximo la infraestructura SDD existente sin duplicar lógica.
  2. El mecanismo de override por tipo de proyecto (`project_types` en registry.yaml)
     es extensible a futuros tipos sin modificar el núcleo del harness.
  3. Los assets LaTeX solo se copian condicionalmente (no para otros tipos de proyecto),
     cumpliendo el requisito de eficiencia de memoria.
- **Alternatives Considered:**
  1. Crear un comando `/expose` separado → Descartado: duplica el flujo SDD y
     fragmenta la experiencia del usuario.
  2. Crear un harness separado → Descartado: fragmenta el ecosistema de herramientas.
  3. Usar archivo `.antigravity.yml` separado → Descartado: toda la configuración
     debe estar centralizada en `harness-config.yaml`.
- **Design Rules Established:**
  - Los datos del expositor (título, autor, institución, fecha) SIEMPRE se preguntan
    explícitamente al usuario. NUNCA se infieren de la fuente de contenido.
    El autor de la fuente ≠ el expositor. El título de la fuente ≠ el título de la expo.
  - Idioma por defecto: español (es). Cambio solo con confirmación humana explícita.
    El idioma de la fuente NO determina el idioma de los entregables.
  - Compilación LaTeX: verificar disponibilidad del compilador antes de intentar.
    Si no está disponible: preguntar al usuario, ofrecer instalación, fallback a solo .tex.
  - Lectura de fuentes: LLM para papers, HTTP README para repos (clonar solo si necesario).
- **Files Affected:**
  - Nuevos: `project_types/exposition/README.md`, `spec_template.md`, `plan_template.md`,
    `tasks_template.md`, `templates/presentacion.tex`, `templates/beamercolorthemeaggie.sty`,
    `templates/presentacion.bib`, `templates/IICO-LOGO-AZUL.png`, `templates/UASLP-LOGO-AZUL.png`
  - Modificados: `harness-config.yaml`, `workflows/registry.yaml`,
    `workflows/sdd-lifecycle.md`, `ANTIGRAVITY.md`, `README.md`,
    `workflows/commands/specify.md`, `workflows/commands/plan.md`,
    `workflows/commands/implement.md`, `memory/decision-log.md`
- **Related:** N/A (primera extensión de tipo de proyecto en el harness)

