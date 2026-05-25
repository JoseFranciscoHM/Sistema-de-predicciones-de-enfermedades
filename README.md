# Antigravity SDD Harness

> **Specification-Driven Development** — A structured methodology that converts human intentions into executable specifications before writing any code.

## What is SDD?

The SDD (Specification-Driven Development) Harness is a self-contained set of rules, workflows, and templates that guide an AI agent (Antigravity) through a disciplined software development lifecycle:

1. **Specify** → Understand the problem and create a formal specification
2. **Plan** → Design the technical implementation
3. **Implement** → Build with TDD (Test-Driven Development)
4. **Review** → Validate against quality gates

Every phase requires **explicit human approval** before proceeding, ensuring no ambiguity slips into the codebase.

---

## Quickstart: Activating the Harness in a New Project

### Step 1: Clone the Harness into your project

```bash
git clone https://github.com/Marianinpb/antigravity-sdd-harness.git .antigravity/harness
```

### Step 2: Copy the activation file

Copy `ANTIGRAVITY.md` from the harness root to the **root of your project**:

```bash
cp .antigravity/harness/ANTIGRAVITY.md ./ANTIGRAVITY.md
```

### Step 3: Configure your project

Edit `.antigravity/harness/harness-config.yaml` to define your project's name, type, tech stack, and security profile.

### Step 4: Start working

Open the project in your IDE with Antigravity. The agent will read `ANTIGRAVITY.md` and activate the SDD workflow automatically.

Use these commands to navigate the lifecycle:
- `/specify` — Start Phase 1: Discovery and Specification
- `/plan` — Start Phase 2: Design and Planning
- `/implement` — Start Phase 3: Implementation (TDD)
- `/review` — Trigger quality gates and code review

---

## Repository Structure

```
antigravity-sdd-harness/
├── README.md                    # This file
├── harness-config.yaml          # Project configuration (generic template)
├── constitution.md              # Non-negotiable development principles
├── ANTIGRAVITY.md               # Activation file (copy to project root)
├── github-config.yaml           # GitHub repository configuration
│
├── templates/                   # Document generation templates
│   ├── spec-template.md         # Specification template (RFC-2119)
│   ├── plan-template.md         # Implementation plan template
│   ├── tasks-template.md        # Task breakdown template
│   └── data-model-template.md   # Data model definition template
│
├── rules/                       # Domain rules and quality criteria
│   ├── security-rules.md        # Security rules (multi-profile)
│   ├── coding-standards.md      # Coding conventions and naming
│   └── quality-gates.json       # Automated quality checks (multi-language)
│
├── workflows/                   # Agent workflow definitions
│   ├── sdd-lifecycle.md         # Main lifecycle (the master document)
│   ├── commands/                # High-level command definitions
│   │   ├── specify.md
│   │   ├── plan.md
│   │   ├── implement.md
│   │   └── review.md
│   └── registry.yaml            # Command-to-workflow mapping
│
└── memory/                      # Project context and decision history
    ├── project-context.md       # High-level project context (fill per project)
    └── decision-log.md          # Immutable decision log

└── project_types/               # Plantillas para tipos de proyecto especializados
    └── exposition/              # Presentaciones académicas (LaTeX beamer)
        ├── README.md            # Documentación del módulo
        ├── spec_template.md     # Plantilla de especificación
        ├── plan_template.md     # Plantilla de plan de implementación
        ├── tasks_template.md    # Plantilla de desglose de tareas
        └── templates/           # Assets LaTeX (se copian condicionalmente)
            ├── presentacion.tex # Plantilla LaTeX parametrizada con placeholders
            ├── beamercolorthemeaggie.sty
            ├── presentacion.bib
            ├── IICO-LOGO-AZUL.png
            └── UASLP-LOGO-AZUL.png
```

---

## Security Profiles

The harness supports multiple security profiles configured via `harness-config.yaml`:

| Profile | Default For | Focus |
|---------|------------|-------|
| `embedded` | Firmware, microcontrollers, FPGA | Memory safety, input validation, no hardcoded secrets |
| `data-science` | ML/AI, data analysis, notebooks | Data privacy, API key management, reproducibility |
| `web` | APIs, web applications | OAuth 2.0, SQL injection prevention, error handling |
| `custom` | Anything else | User-defined rules |

---

## Tipos de Proyecto Especializados

El harness soporta tipos de proyecto con plantillas y flujos adaptados que se
integran en el ciclo SDD estándar sin introducir comandos nuevos.

| Tipo | Descripción | Entregables | Documentación |
|------|-------------|-------------|---------------|
| `exposition` | Presentaciones académicas | Resumen, presentación LaTeX, guion | `project_types/exposition/README.md` |

Para activar un tipo especializado, establece `project.type` en `harness-config.yaml`
al valor correspondiente. Las plantillas genéricas son sobreescritas automáticamente
por las del tipo de proyecto. Los assets adicionales (p.ej. archivos LaTeX) solo
se copian cuando la tarea correspondiente lo indica, no al inicio del proyecto.


---

## Supported Languages (Quality Gates)

Out of the box, quality gates are configured for:

- **Python** — ruff, pytest, mypy
- **C** — gcc/idf.py, cppcheck
- **VHDL** — ghdl, Quartus
- **Verilog** — iverilog, Quartus
- **LaTeX** — pdflatex, latexmk
- **MATLAB** — mlint
- **Mathematica** — wolframscript

---

## Contributing / Forking

This harness is designed to be **forked and customized**. Each team member can:

1. Fork this repository
2. Create a personal branch
3. Customize rules, templates, and quality gates
4. Share improvements via pull requests

---

## License

This project is provided as-is for educational and development purposes.

---

## Despliegue

### Backend (PythonAnywhere)
1. Sube el repositorio a GitHub
2. En PythonAnywhere: Web → Add new app → ASGI → Python 3.11
3. Clona el repo: `git clone https://github.com/TU-USUARIO/SDD.git`
4. Crea virtualenv: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
5. Genera datos: `cd SDD && PYTHONPATH=src python src/seed_all.sh`
6. Configura WSGI como: `wsgi.application` (archivo `wsgi.py` ya incluido)
7. Static files: `/static/` → `/home/tu-usuario/SDD/static/`

### Frontend (GitHub Pages)
1. Ve a Settings → Pages → Source: "GitHub Actions"
2. El workflow `.github/workflows/deploy.yml` despliega `static/` automaticamente
3. Configura la URL del backend en GitHub Pages:
   - En `static/index.html`, agrega antes de `</head>`:
     `<script>window.API_BASE_URL = "https://tu-app.pythonanywhere.com";</script>`
   - O usa el archivo `static/js/config.js` ya incluido
