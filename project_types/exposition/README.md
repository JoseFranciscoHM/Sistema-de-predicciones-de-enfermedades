# Módulo de Tipo de Proyecto: Exposición

> **Tipo:** `exposition`
> **Versión:** 1.0.0
> **Parte del:** Harness SDD Antigravity

---

## ¿Qué es este módulo?

El módulo `exposition` extiende el harness SDD Antigravity para soportar la
generación automática de presentaciones académicas. Dado un tema y su fuente
de contenido (paper, libro de referencia, o repositorio), el agente genera
automáticamente tres entregables listos para usar:

1. **Resumen** — Síntesis estructurada del contenido de la fuente.
2. **Presentación LaTeX** — Diapositivas en formato beamer con plantilla institucional.
3. **Guion de exposición** — Narración sugerida alineada con cada diapositiva.

El módulo **no introduce comandos nuevos**: funciona con el flujo SDD estándar
(`/specify → /plan → /implement`), pero carga plantillas especializadas cuando
detecta `project.type: exposition` en `harness-config.yaml`.

---

## Cómo activar el módulo

### 1. Configurar `harness-config.yaml`

Establece el tipo de proyecto y la sección de exposición:

```yaml
project:
  name: "Mi Exposición de Filtros Adaptativos"
  type: "exposition"
  description: "Exposición académica sobre filtros de Wiener y LMS"

exposition:
  # Fuente de contenido (usar SOLO UNA):
  paper_path: "docs/paper.pdf"        # Opción 1: ruta a un PDF
  topic: ""                            # Opción 2: tema libre
  book_reference: ""                   # Opción 2: libro de referencia (con topic)
  repo_url: ""                         # Opción 3: repositorio

  # Datos del expositor (el agente los preguntará explícitamente):
  title: ""
  subtitle: ""
  author: ""
  institution: ""
  date: ""
  estimated_duration: ""
  audience: ""
  language: "es"                       # "es" por defecto. Cambiar solo con confirmación explícita.
```

### 2. Iniciar el flujo SDD

Con el harness activado, ejecuta los comandos en orden:

```
/specify  — El agente solicita datos del expositor y genera la especificación
/plan     — El agente diseña el plan con las 4 fases predefinidas
/implement — El agente ejecuta las tareas y genera los entregables
```

---

## Reglas críticas del módulo

> [!IMPORTANT]
> ### Regla 1: Los datos del expositor SIEMPRE se preguntan
>
> El agente NUNCA debe inferir el nombre del expositor, la institución, ni el
> título de la presentación del contenido de la fuente.
>
> El autor del paper ≠ el expositor.
> El título del paper ≠ el título de la exposición.
> La institución de los autores ≠ la institución del expositor.
>
> **El agente DEBE preguntar explícitamente CADA campo al usuario.**

> [!IMPORTANT]
> ### Regla 2: El idioma de los entregables es español por defecto
>
> Aunque la fuente (paper, repositorio) esté en inglés u otro idioma, los
> entregables se generan en ESPAÑOL a menos que el usuario confirme explícitamente
> un cambio de idioma.
>
> El agente NO debe inferir el idioma del idioma de la fuente.

> [!CAUTION]
> ### Regla 3: Los assets LaTeX solo se copian para proyectos exposition
>
> Los archivos en `project_types/exposition/templates/` SOLO se copian al
> directorio `presentacion/` del proyecto cuando el tipo de proyecto es
> `exposition`. No deben copiarse en ningún otro contexto.

---

## Fuentes de contenido soportadas

### Opción 1: Paper (PDF)

Configura `paper_path` con la ruta al PDF del artículo académico.

```yaml
exposition:
  paper_path: "docs/mi_paper.pdf"
```

El agente leerá el PDF con sus capacidades LLM para extraer el contenido.
Si no puede extraer información suficiente, preguntará al usuario los puntos clave.

### Opción 2: Tema + libro de referencia

Configura `topic` con el tema de la exposición y `book_reference` con la
referencia bibliográfica del libro que servirá como fuente principal.

```yaml
exposition:
  topic: "Filtros Adaptativos"
  book_reference: "Farhang-Boroujeny, B. (2013). Adaptive Filters: Theory and Applications"
```

### Opción 3: Repositorio

Configura `repo_url` con la URL del repositorio a analizar.

```yaml
exposition:
  repo_url: "https://github.com/usuario/mi-proyecto"
```

El agente leerá el README y la documentación disponible vía HTTP. Solo clonará
el repositorio si es necesario para acceder a assets específicos (imágenes,
datos) que no están disponibles en los documentos en línea.

---

## Entregables generados

| Entregable | Ruta | Generado en |
|------------|------|-------------|
| Especificación | `specs/SPEC-XX-exposicion.md` | `/specify` |
| Plan | `plans/PLAN-XX-exposicion.md` | `/plan` |
| Tareas | `tasks/TASKS-XX-exposicion.md` | `/plan` |
| Resumen del contenido | `resumen_paper.md` / `resumen_tema.md` / `resumen_proyecto.md` | TASK-03 |
| Presentación LaTeX | `presentacion/presentacion.tex` | TASK-05 |
| PDF de la presentación | `presentacion/presentacion.pdf` | TASK-06 (si compilador disponible) |
| Guion de exposición | `guion_exposicion.md` | TASK-07 |

---

## Compilación LaTeX

El módulo verifica automáticamente si hay un compilador de LaTeX disponible:

1. Busca `pdflatex` o `latexmk` en el sistema.
2. Si no está disponible, pregunta al usuario si desea instalarlo.
3. Si el usuario no quiere instalar, genera solo el `.tex` listo para compilar manualmente.

**Instrucciones de compilación manual:**
```bash
cd presentacion
pdflatex presentacion.tex
bibtex presentacion
pdflatex presentacion.tex
pdflatex presentacion.tex
```

---

## Estructura de archivos del módulo

```
project_types/exposition/
├── README.md                        # Este archivo
├── spec_template.md                 # Plantilla de especificación
├── plan_template.md                 # Plantilla de plan de implementación
├── tasks_template.md                # Plantilla de desglose de tareas
└── templates/                       # Assets LaTeX (no copiar manualmente)
    ├── presentacion.tex             # Plantilla LaTeX con placeholders
    ├── beamercolorthemeaggie.sty    # Tema de colores institucional (UASLP)
    ├── presentacion.bib             # Bibliografía base
    ├── IICO-LOGO-AZUL.png           # Logo del IICO
    └── UASLP-LOGO-AZUL.png         # Logo de la UASLP
```

---

## Placeholders de la plantilla LaTeX

| Placeholder | Descripción | Fuente |
|-------------|-------------|--------|
| `{{TITULO}}` | Título principal de la presentación | Usuario (explícito) |
| `{{SUBTITULO}}` | Subtítulo (opcional) | Usuario (explícito) |
| `{{AUTOR}}` | Nombre del expositor | Usuario (explícito) |
| `{{INSTITUCION}}` | Institución académica | Usuario (explícito) |
| `{{FECHA}}` | Fecha de presentación | Usuario (explícito) |
| `{{CONTENIDO_SECCIONES}}` | Secciones y frames | Generado por el agente a partir de la fuente |

---

## Ejemplo de configuración completa

```yaml
project:
  name: "Exposicion-Filtros-Adaptativos"
  type: "exposition"
  description: "Presentación académica sobre filtros de Wiener y el algoritmo LMS"

environment:
  tech_stack: ["latex"]
  package_manager: ""

exposition:
  paper_path: ""
  topic: "Filtros Adaptativos"
  book_reference: "Farhang-Boroujeny, B. (2013). Adaptive Filters: Theory and Applications. Wiley."
  repo_url: ""

  # Estos campos se llenan DESPUÉS de que el agente los pregunta al usuario:
  title: "Filtros Adaptativos: Teoría y Aplicaciones"
  subtitle: "Filtros de Wiener y Algoritmo LMS"
  author: "Mariano Prado Berman"
  institution: "Instituto de Investigación en Comunicación Óptica (IICO) \\\\ Universidad Autónoma de San Luis Potosí (UASLP)"
  date: "2026-05-23"
  estimated_duration: "20 min"
  audience: "Maestría en Ciencias de la Ingeniería"
  language: "es"
```

---

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-05-23 | Primera versión del módulo |
