# Plan de Implementación: [PLAN-ID] Exposición — [Título de la Exposición]

> **Estado:** Borrador | En Revisión | Aprobado
> **Especificación:** [Enlace a la spec aprobada: specs/SPEC-XX-exposicion.md]
> **Autor:** [Nombre del expositor — dato proporcionado explícitamente por el usuario]
> **Fecha:** [YYYY-MM-DD]
> **Aprobado por:** [Nombre] el [YYYY-MM-DD]

---

## 1. Resumen

Este plan describe cómo se generarán los entregables de la exposición académica
a partir de la fuente de contenido especificada. El proceso sigue el flujo SDD
estándar pero con plantillas y tareas predefinidas para el tipo `exposition`.

**Enfoque técnico:**
El agente analiza la fuente de contenido con sus capacidades LLM, extrae los
conceptos clave, y los transforma en tres entregables: resumen, presentación
LaTeX y guion de exposición.

**Datos del expositor (obtenidos explícitamente del usuario):**

| Campo | Valor |
|-------|-------|
| Nombre del expositor | [Valor confirmado por el usuario] |
| Institución | [Valor confirmado por el usuario] |
| Título de la exposición | [Valor confirmado por el usuario] |
| Subtítulo | [Valor confirmado por el usuario] |
| Fecha | [Valor confirmado por el usuario] |
| Audiencia | [Valor confirmado por el usuario] |
| Duración estimada | [Valor confirmado por el usuario] |
| Idioma | Español (por defecto) |

**Tipo de fuente activa:** [paper | tema+libro | repositorio]

---

## 2. Arquitectura de los Entregables

```
proyecto/
├── specs/
│   └── SPEC-XX-exposicion.md       (generado en /specify)
├── plans/
│   └── PLAN-XX-exposicion.md       (este archivo)
├── tasks/
│   └── TASKS-XX-exposicion.md      (generado en /plan)
├── resumen_{fuente}.md             (generado en TASK-03)
├── guion_exposicion.md             (generado en TASK-07)
└── presentacion/
    ├── presentacion.tex            (generado en TASK-05)
    ├── presentacion.pdf            (generado en TASK-06, si compilador disponible)
    ├── beamercolorthemeaggie.sty   (copiado en TASK-04)
    ├── presentacion.bib            (copiado en TASK-04)
    ├── IICO-LOGO-AZUL.png          (copiado en TASK-04)
    └── UASLP-LOGO-AZUL.png        (copiado en TASK-04)
```

---

## 3. Tecnologías y Herramientas

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Presentación | LaTeX (beamer, metropolis) | Plantilla institucional probada |
| Tema visual | beamercolorthemeaggie | Colores institucionales UASLP/IICO |
| Compilación | pdflatex / latexmk | Estándar de distribuciones LaTeX |
| Resumen y guion | Markdown | Legible y editable sin herramientas especiales |
| Análisis de fuente | Capacidades LLM del agente | Sin dependencias externas adicionales |

---

## 4. Desglose de Tareas

_Cada tarea incluye `_Boundary_` y `_Depends_`. Ver `tasks/TASKS-XX-exposicion.md`._

### Fase A: Recolección de datos del expositor

#### Tarea 1: Solicitar datos al expositor
- **ID:** TASK-01
- **_Boundary_:** Solo interacción con el usuario para recopilar datos de la presentación.
  No modifica ningún archivo.
- **_Depends_:** None
- **Descripción:** El agente solicita EXPLÍCITAMENTE al usuario cada uno de los campos
  del expositor (título, autor, institución, fecha, audiencia, duración). NUNCA
  infiere estos datos de la fuente.
- **Tests/Verificación:** Confirmación visual de que todos los campos fueron provistos
  por el usuario antes de proceder.
- **Complejidad:** Baja

---

### Fase B: Análisis de la fuente y generación de resumen

#### Tarea 2: Leer y analizar la fuente de contenido
- **ID:** TASK-02
- **_Boundary_:** Lectura de la fuente especificada en `harness-config.yaml`. No genera
  archivos aún.
- **_Depends_:** TASK-01
- **Descripción:**
  - Si `paper_path`: leer el PDF con capacidades LLM. Extraer título del paper,
    autores del paper, abstract, conceptos clave, estructura del documento.
    Si no puede extraer, preguntar al usuario los datos clave.
  - Si `topic` + `book_reference`: usar el tema y la referencia del libro como
    base para estructurar el contenido.
  - Si `repo_url`: leer README y documentación disponible vía HTTP. Determinar
    si es necesario clonar (solo si hay assets necesarios no disponibles en docs).
- **Tests/Verificación:** El agente puede describir los conceptos clave de la fuente.
- **Complejidad:** Media

#### Tarea 3: Generar resumen del contenido
- **ID:** TASK-03
- **_Boundary_:** Solo crea/modifica `resumen_{fuente}.md`.
- **_Depends_:** TASK-02
- **Descripción:** Generar un resumen estructurado del contenido analizado.
  El nombre del archivo depende de la fuente:
  - `paper_path` → `resumen_paper.md`
  - `topic`+`book_reference` → `resumen_tema.md`
  - `repo_url` → `resumen_proyecto.md`
  El resumen debe ser coherente, bien estructurado y en el idioma configurado.
- **Tests/Verificación:** El archivo existe y contiene secciones coherentes con
  la fuente.
- **Complejidad:** Media

---

### Fase C: Generación de la presentación LaTeX

#### Tarea 4: Copiar plantilla LaTeX al directorio del proyecto
- **ID:** TASK-04
- **_Boundary_:** Solo copia archivos de `project_types/exposition/templates/`
  al directorio `presentacion/` del proyecto. No modifica ningún archivo.
- **_Depends_:** TASK-01
- **Descripción:** Copiar condicionalmente los assets LaTeX:
  - `presentacion.tex` → `presentacion/presentacion.tex`
  - `beamercolorthemeaggie.sty` → `presentacion/beamercolorthemeaggie.sty`
  - `presentacion.bib` → `presentacion/presentacion.bib`
  - `IICO-LOGO-AZUL.png` → `presentacion/IICO-LOGO-AZUL.png`
  - `UASLP-LOGO-AZUL.png` → `presentacion/UASLP-LOGO-AZUL.png`
  IMPORTANTE: Solo copiar si el proyecto es de tipo `exposition`.
- **Tests/Verificación:** Los 5 archivos existen en `presentacion/`.
- **Complejidad:** Baja

#### Tarea 5: Reemplazar placeholders y generar contenido de diapositivas
- **ID:** TASK-05
- **_Boundary_:** Solo modifica `presentacion/presentacion.tex`.
- **_Depends_:** TASK-03, TASK-04
- **Descripción:**
  1. Reemplazar los placeholders de metadatos con los datos del usuario:
     - `{{TITULO}}` → título de la exposición
     - `{{SUBTITULO}}` → subtítulo (o eliminar la línea si está vacío)
     - `{{AUTOR}}` → nombre del expositor
     - `{{INSTITUCION}}` → institución del expositor
     - `{{FECHA}}` → fecha de la presentación
  2. Generar el contenido de las secciones y frames (`{{CONTENIDO_SECCIONES}}`)
     a partir del resumen generado en TASK-03. Cada concepto clave se convierte
     en una sección con sus frames correspondientes.
  3. Verificar que NO quede ningún placeholder `{{...}}` sin reemplazar.
- **Tests/Verificación:** El archivo `.tex` no contiene la cadena `{{`. Todos los
  metadatos visibles corresponden a datos del usuario.
- **Complejidad:** Alta

#### Tarea 6: Compilar la presentación a PDF (condicional)
- **ID:** TASK-06
- **_Boundary_:** Solo genera `presentacion/presentacion.pdf`. No modifica `.tex`.
- **_Depends_:** TASK-05
- **Descripción:**
  1. Verificar disponibilidad de `pdflatex` o `latexmk` en el sistema.
  2. Si disponible: compilar con `cd presentacion && pdflatex presentacion.tex`.
     Si hay errores de bibliografía, ejecutar `bibtex presentacion` y recompilar.
  3. Si NO disponible: preguntar al usuario si desea instalar el compilador.
     - Si acepta: intentar instalación.
     - Si rechaza: informar que el `.tex` está listo para compilación manual.
- **Tests/Verificación:** Existe `presentacion/presentacion.pdf` sin errores de compilación,
  o el usuario fue informado de por qué no se generó el PDF.
- **Complejidad:** Media

---

### Fase D: Generación del guion de exposición

#### Tarea 7: Generar guion alineado con las diapositivas
- **ID:** TASK-07
- **_Boundary_:** Solo crea/modifica `guion_exposicion.md`.
- **_Depends_:** TASK-05
- **Descripción:** Generar el guion de la exposición alineado con las diapositivas
  generadas. Para cada frame de la presentación, el guion incluye:
  - Acción (qué hacer con la diapositiva)
  - Narración (qué decir al presentar ese contenido)
  El guion debe estar en el idioma configurado y adaptado a la audiencia y duración.
- **Tests/Verificación:** El archivo existe. Cada sección de la presentación tiene
  al menos un bloque en el guion.
- **Complejidad:** Media

---

## 5. Dependencias Externas

| Dependencia | Versión | Propósito | ¿Nueva? |
|-------------|---------|-----------|---------|
| pdflatex | Cualquiera | Compilación LaTeX | Solo si no instalado |
| latexmk | Cualquiera | Alternativa de compilación | Solo si no instalado |
| beamer (LaTeX) | Cualquiera | Clase de presentación | Incluido en TeX Live |
| metropolis (beamer theme) | Cualquiera | Tema visual de la presentación | Incluido en TeX Live |

---

## 6. Estrategia de Manejo de Errores

| Escenario | Estrategia | Impacto en el usuario |
|-----------|-----------|----------------------|
| No puede leer el PDF | Preguntar al usuario los datos clave | Mínimo: el usuario provee el resumen |
| Compilador LaTeX no disponible | Preguntar, ofrecer instalar, si no: solo .tex | Bajo: puede compilar manualmente |
| URL del repo no accesible | Informar al usuario y pedir alternativa | Mínimo: el usuario provee el contenido |
| Placeholder sin reemplazar | Detener y reportar error antes de compilar | Bajo: el agente lo corrige |
| Compilación LaTeX falla | Reportar error de LaTeX, no marcar como completo | Bajo: el agente intenta corregir |

---

## 7. Notas de Implementación

> **Nota:** Esta sección se completa DURANTE la fase `/implement`. Las notas son
> de solo lectura — no eliminar entradas existentes.

### [Fecha] — [ID de Tarea]
- [Nota sobre lo aprendido o lo que cambió]

---

## 8. Plan de Verificación

### Verificación automática
- `[ ]` El archivo `resumen_{fuente}.md` existe y tiene contenido estructurado.
- `[ ]` Los 5 archivos de la plantilla LaTeX existen en `presentacion/`.
- `[ ]` `presentacion.tex` no contiene la cadena `{{`.
- `[ ]` Si se compiló: `presentacion.pdf` existe y es un PDF válido.
- `[ ]` `guion_exposicion.md` tiene al menos una sección por cada sección de la presentación.

### Verificación manual
- `[ ]` Revisar que el contenido del resumen es coherente con la fuente.
- `[ ]` Revisar que los datos del expositor en la presentación son correctos.
- `[ ]` Revisar que el guion está alineado con las diapositivas.

---

## 9. Plan de Rollback

- Los assets LaTeX se copian desde `project_types/exposition/templates/`, por lo que
  pueden eliminarse y recopiarse en cualquier momento.
- Los archivos generados (resumen, presentación, guion) pueden regenerarse ejecutando
  `/implement` nuevamente desde la tarea correspondiente.
