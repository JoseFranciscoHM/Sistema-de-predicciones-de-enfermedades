# Desglose de Tareas: Exposición — [Título de la Exposición]

> **Plan de referencia:** [Enlace al plan aprobado: plans/PLAN-XX-exposicion.md]
> **Fecha:** [YYYY-MM-DD]
> **Total de tareas:** 7

---

## Leyenda de estado

- `[ ]` — No iniciada
- `[/]` — En progreso
- `[x]` — Completada
- `[!]` — Bloqueada (ver notas al final)

---

> [!IMPORTANT]
> **REGLA CRÍTICA ANTES DE COMENZAR:** El agente DEBE completar TASK-01
> (solicitar datos del expositor) antes de proceder con cualquier otra tarea.
> Los datos del expositor (título, autor, institución, fecha) NUNCA se infieren
> del contenido de la fuente. SIEMPRE se preguntan explícitamente al usuario.

---

## Fase A: Recolección de datos del expositor

- `[ ]` **TASK-01:** Solicitar datos del expositor al usuario
  - **_Boundary_:** Solo interacción con el usuario. No crea ni modifica archivos.
  - **_Depends_:** None
  - **Descripción:** Solicitar EXPLÍCITAMENTE al usuario los siguientes datos antes
    de cualquier generación de contenido:
    1. ¿Cuál es tu nombre completo (como aparecerá en la presentación)?
    2. ¿Cuál es tu institución académica?
    3. ¿Cuál es el título de tu exposición?
    4. ¿Tiene subtítulo? (puede ser vacío)
    5. ¿Cuál es la fecha de presentación?
    6. ¿A quién va dirigida la exposición (audiencia)?
    7. ¿Cuánto tiempo tienes para presentar?
    8. ¿El contenido debe generarse en español? (confirmar antes de cambiar el idioma)
  - **Criterios de aceptación:**
    - [ ] Todos los campos obligatorios fueron provistos por el usuario.
    - [ ] El agente NO usó ningún dato inferido de la fuente como respuesta.
    - [ ] El idioma fue confirmado (español por defecto).
  - **Tests/Verificación:** Confirmación visual — el agente lista los datos recibidos
    y el usuario los confirma antes de continuar.
  - **Complejidad:** Baja

---

## Fase B: Análisis de la fuente y generación de resumen

- `[ ]` **TASK-02:** Leer y analizar la fuente de contenido
  - **_Boundary_:** Solo lectura de la fuente. No crea ni modifica archivos.
  - **_Depends_:** TASK-01
  - **Descripción según tipo de fuente:**
    - **paper** (`paper_path` configurado): Leer el PDF con capacidades LLM.
      Extraer: título del paper (≠ título de la exposición), autores del paper
      (≠ expositor), resumen/abstract, conceptos principales, estructura del documento.
      Si la lectura falla o es insuficiente, preguntar al usuario los puntos clave.
    - **tema+libro** (`topic` + `book_reference`): Identificar los conceptos clave
      del tema especificado, usando el libro como fuente de autoridad.
    - **repositorio** (`repo_url`): Acceder al README y docs vía HTTP.
      Identificar propósito del proyecto, tecnologías, estructura, resultados.
      Solo proponer clonar si los docs mencionan assets necesarios (gráficas,
      ejemplos de código específicos) que no están disponibles en el README.
  - **Criterios de aceptación:**
    - [ ] El agente puede describir los 3-5 conceptos principales de la fuente.
    - [ ] El agente tiene suficiente información para generar el resumen.
  - **Tests/Verificación:** El agente presenta un listado de conceptos clave al
    usuario y espera confirmación de que son correctos.
  - **Complejidad:** Media
  - **Notas:** [Completar durante `/implement`]

- `[ ]` **TASK-03:** Generar resumen del contenido
  - **_Boundary_:** Solo crea/modifica el archivo de resumen correspondiente.
  - **_Depends_:** TASK-02
  - **Descripción:** Generar un resumen estructurado en Markdown del contenido
    analizado. Nombre del archivo según la fuente:
    - `paper_path` → `resumen_paper.md`
    - `topic`+`book_reference` → `resumen_tema.md`
    - `repo_url` → `resumen_proyecto.md`
    El resumen debe incluir: contexto/motivación, conceptos clave (con explicaciones),
    fórmulas o estructuras relevantes (si aplica), conclusiones principales.
    El resumen debe estar en el idioma configurado.
  - **Criterios de aceptación:**
    - [ ] El archivo existe en la raíz del proyecto con el nombre correcto.
    - [ ] Tiene al menos 3 secciones estructuradas con contenido sustancial.
    - [ ] El contenido está en el idioma configurado.
    - [ ] Es coherente con la fuente analizada.
  - **Tests/Verificación:** Revisión del agente del resumen antes de continuar.
  - **Complejidad:** Media

---

## Fase C: Generación de la presentación LaTeX

- `[ ]` **TASK-04:** Copiar plantilla LaTeX al directorio del proyecto
  - **_Boundary_:** Solo copia archivos de `project_types/exposition/templates/`
    al directorio `presentacion/` del proyecto. No modifica ningún archivo.
  - **_Depends_:** TASK-01
  - **Descripción:** Crear el directorio `presentacion/` si no existe, y copiar
    los siguientes archivos:
    - `presentacion.tex` (plantilla con placeholders)
    - `beamercolorthemeaggie.sty` (tema de colores)
    - `presentacion.bib` (bibliografía base)
    - `IICO-LOGO-AZUL.png` (logo IICO)
    - `UASLP-LOGO-AZUL.png` (logo UASLP)
  - **Criterios de aceptación:**
    - [ ] El directorio `presentacion/` existe.
    - [ ] Los 5 archivos existen en `presentacion/`.
    - [ ] `presentacion.tex` contiene los placeholders `{{TITULO}}`, `{{AUTOR}}`, etc.
  - **Tests/Verificación:** Verificar existencia de los archivos con listado de directorio.
  - **Complejidad:** Baja

- `[ ]` **TASK-05:** Reemplazar placeholders y generar contenido de diapositivas
  - **_Boundary_:** Solo modifica `presentacion/presentacion.tex`.
  - **_Depends_:** TASK-03, TASK-04
  - **Descripción:**
    1. Reemplazar placeholders de metadatos con datos del usuario (TASK-01):
       - `{{TITULO}}` → título de la exposición (provisto por usuario)
       - `{{SUBTITULO}}` → subtítulo (provisto por usuario; eliminar línea si vacío)
       - `{{AUTOR}}` → nombre del expositor (provisto por usuario)
       - `{{INSTITUCION}}` → institución (provista por usuario)
       - `{{FECHA}}` → fecha de presentación (provista por usuario)
    2. Generar el contenido LaTeX de las secciones (`{{CONTENIDO_SECCIONES}}`)
       a partir del resumen (TASK-03). Cada concepto principal → una `\section{}`.
       Cada punto clave dentro de un concepto → un `\begin{frame}{}...\end{frame}`.
       Incluir ecuaciones con entornos `equation` si aplica.
    3. Verificar que NO existe ninguna cadena `{{` en el archivo resultante.
  - **Criterios de aceptación:**
    - [ ] El archivo no contiene la cadena `{{`.
    - [ ] Los metadatos son los provistos por el usuario (no inferidos de la fuente).
    - [ ] Hay al menos una sección con al menos un frame por cada concepto principal.
    - [ ] El contenido está en el idioma configurado.
  - **Tests/Verificación:** Búsqueda de `{{` en el archivo; revisión de metadatos.
  - **Complejidad:** Alta
  - **Notas:** [Completar durante `/implement`]

- `[ ]` **TASK-06:** Compilar la presentación a PDF (condicional)
  - **_Boundary_:** Solo genera `presentacion/presentacion.pdf`. No modifica `.tex`.
  - **_Depends_:** TASK-05
  - **Descripción:**
    1. Verificar si `pdflatex` está disponible: `pdflatex --version`.
    2. Si no está disponible, verificar `latexmk`: `latexmk --version`.
    3. Si ninguno está disponible:
       a. Preguntar: "¿Tienes un compilador de LaTeX instalado en tu sistema?"
       b. Si dice no: "¿Deseas que intente instalarlo? (requiere conexión a internet)"
       c. Si acepta: intentar instalación según SO.
       d. Si rechaza: informar que `presentacion.tex` está listo para compilación
          manual (instrucciones: `cd presentacion && pdflatex presentacion.tex`).
    4. Si el compilador está disponible: compilar con 2 pasadas para referencias.
       Si hay bibliografía, ejecutar `bibtex` entre pasadas.
  - **Criterios de aceptación:**
    - [ ] Si compilador disponible: `presentacion.pdf` existe y es un PDF válido.
    - [ ] Si compilador no disponible: el usuario fue informado con instrucciones claras.
    - [ ] En caso de error de compilación: el error fue reportado al usuario.
  - **Tests/Verificación:** Verificar existencia del PDF o confirmación al usuario.
  - **Complejidad:** Media

---

## Fase D: Generación del guion de exposición

- `[ ]` **TASK-07:** Generar guion de exposición alineado con las diapositivas
  - **_Boundary_:** Solo crea/modifica `guion_exposicion.md`.
  - **_Depends_:** TASK-05
  - **Descripción:** Generar el guion de la exposición en Markdown. Para cada
    sección y frame de la presentación, incluir:
    - `## Diapositiva N: [Título del Frame]`
    - `**[Acción]** *Qué hacer al mostrar esta diapositiva*`
    - `**[Narración]** "Texto sugerido para hablar"` (en primera persona, fluido,
      adaptado a la audiencia y duración especificadas en TASK-01)
    El guion debe estar en el idioma configurado y ser coherente con el contenido
    de las diapositivas generadas en TASK-05.
  - **Criterios de aceptación:**
    - [ ] El archivo `guion_exposicion.md` existe.
    - [ ] Tiene una sección por cada frame de la presentación.
    - [ ] El tono es apropiado para la audiencia indicada.
    - [ ] El contenido está en el idioma configurado.
    - [ ] La narración está en primera persona y fluye naturalmente.
  - **Tests/Verificación:** Comparar el número de secciones del guion con el
    número de frames en el `.tex`.
  - **Complejidad:** Media

---

## Resumen de progreso

| Fase | Total | Hecha | En progreso | Bloqueada |
|------|-------|-------|-------------|-----------|
| A — Datos del expositor | 1 | 0 | 0 | 0 |
| B — Análisis y resumen | 2 | 0 | 0 | 0 |
| C — Presentación LaTeX | 3 | 0 | 0 | 0 |
| D — Guion | 1 | 0 | 0 | 0 |
| **Total** | **7** | **0** | **0** | **0** |

---

## Registro de tareas bloqueadas

_Registrar aquí cualquier tarea bloqueada y la razón del bloqueo._

| ID de Tarea | Bloqueada desde | Razón | Resolución |
|-------------|----------------|-------|------------|
| — | — | — | — |
